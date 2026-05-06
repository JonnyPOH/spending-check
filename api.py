import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from src.schema import AnalyseResponse, BroadSummary, NetByPeriod

app = FastAPI(title="Spending Check API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── shared analysis logic ────────────────────────────────────────────────────

def _run_analysis(year: int | None, month: int | None) -> AnalyseResponse:
    """Run the full pipeline against whatever is currently loaded in DuckDB."""
    from src.db import _get_connection
    from src.features import collect_all, monthly_by_category
    from src.llm import get_insights
    from src.pipeline import _last_complete_month
    from src.prompts import SYSTEM, build_user_prompt

    if year is None or month is None:
        year, month = _last_complete_month()

    features = collect_all(year, month)
    report   = get_insights(SYSTEM, build_user_prompt(features, year, month), year, month)
    df_month = monthly_by_category(year, month)
    conn     = _get_connection()

    columns   = [col[0] for col in conn.execute("DESCRIBE transactions").fetchall()]
    broad_col = "broad" if "broad" in columns else "category"
    savings_filter = f"LOWER({broad_col}) != 'savings'"

    df_monthly_net = conn.execute("""
        SELECT strftime(transaction_date, '%Y-%m') AS period,
               ROUND(SUM(amount), 2)               AS net_amount
        FROM transactions
        GROUP BY period ORDER BY period
    """).df()

    df_monthly_net_ex = conn.execute(f"""
        SELECT strftime(transaction_date, '%Y-%m') AS period,
               ROUND(SUM(amount), 2)               AS net_amount
        FROM transactions
        WHERE {savings_filter}
        GROUP BY period ORDER BY period
    """).df()

    df_quarterly_net = conn.execute("""
        SELECT SUBSTR(CAST(year(transaction_date) AS VARCHAR), 3, 2)
                   || '-' || CAST(quarter(transaction_date) AS VARCHAR) AS period,
               ROUND(SUM(amount), 2) AS net_amount
        FROM transactions
        GROUP BY period ORDER BY period
    """).df()

    df_quarterly_net_ex = conn.execute(f"""
        SELECT SUBSTR(CAST(year(transaction_date) AS VARCHAR), 3, 2)
                   || '-' || CAST(quarter(transaction_date) AS VARCHAR) AS period,
               ROUND(SUM(amount), 2) AS net_amount
        FROM transactions
        WHERE {savings_filter}
        GROUP BY period ORDER BY period
    """).df()

    df_broad = conn.execute(f"""
        SELECT {broad_col}                                                         AS broad,
               ROUND(SUM(amount), 2)                                               AS total_amount,
               ROUND(
                   SUM(amount) / COUNT(DISTINCT strftime(transaction_date, '%Y-%m')), 2
               )                                                                   AS avg_per_month
        FROM transactions
        WHERE {broad_col} IS NOT NULL AND {broad_col} != ''
        GROUP BY {broad_col}
        ORDER BY SUM(amount) ASC
    """).df()

    return AnalyseResponse(
        period_year=report.period_year,
        period_month=report.period_month,
        insights=report.insights,
        spend_by_category=df_month.to_dict(orient="records"),
        monthly_net=[NetByPeriod(**r) for r in df_monthly_net.to_dict(orient="records")],
        monthly_net_ex_savings=[NetByPeriod(**r) for r in df_monthly_net_ex.to_dict(orient="records")],
        quarterly_net=[NetByPeriod(**r) for r in df_quarterly_net.to_dict(orient="records")],
        quarterly_net_ex_savings=[NetByPeriod(**r) for r in df_quarterly_net_ex.to_dict(orient="records")],
        broad_summary=[BroadSummary(**r) for r in df_broad.to_dict(orient="records")],
    )


# ── endpoints ────────────────────────────────────────────────────────────────

@app.post("/analyse", response_model=AnalyseResponse)
async def analyse(
    file:  UploadFile  = File(...),
    year:  int | None  = Form(None),
    month: int | None  = Form(None),
):
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        f.write(await file.read())
        tmp_path = Path(f.name)

    from src.db import reset
    reset(tmp_path)

    return _run_analysis(year, month)


@app.get("/connect")
async def connect(redirect_uri: str | None = None):
    """Return the TrueLayer auth URL for the app to open in a browser."""
    from src.truelayer import auth_url
    return {"url": auth_url(redirect_uri), "redirect_uri": redirect_uri}


@app.post("/analyse-from-bank", response_model=AnalyseResponse)
async def analyse_from_bank(
    code:         str       = Form(...),
    redirect_uri: str | None = Form(None),
    year:         int | None = Form(None),
    month:        int | None = Form(None),
):
    """Exchange a TrueLayer auth code, fetch transactions, run the pipeline."""
    from src.truelayer import exchange_code, fetch_transactions
    from src.db import reset_from_df

    access_token = exchange_code(code, redirect_uri)
    df           = fetch_transactions(access_token)
    reset_from_df(df)

    return _run_analysis(year, month)
