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


@app.post("/analyse", response_model=AnalyseResponse)
async def analyse(
    file: UploadFile = File(...),
    year: int | None = Form(None),
    month: int | None = Form(None),
):
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        f.write(await file.read())
        tmp_path = Path(f.name)

    from src.db import _get_connection, reset
    reset(tmp_path)

    from src.features import collect_all, monthly_by_category
    from src.llm import get_insights
    from src.pipeline import _last_complete_month
    from src.prompts import SYSTEM, build_user_prompt

    if year is None or month is None:
        year, month = _last_complete_month()

    features = collect_all(year, month)
    report = get_insights(SYSTEM, build_user_prompt(features, year, month), year, month)
    df_month = monthly_by_category(year, month)

    conn = _get_connection()

    # Detect broad vs category column first — needed for all queries below
    columns = [col[0] for col in conn.execute("DESCRIBE transactions").fetchall()]
    broad_col = "broad" if "broad" in columns else "category"
    savings_filter = f"LOWER({broad_col}) != 'savings'"

    # Net amount per month (income + spending combined)
    df_monthly_net = conn.execute("""
        SELECT
            strftime(transaction_date, '%Y-%m') AS period,
            ROUND(SUM(amount), 2)               AS net_amount
        FROM transactions
        GROUP BY period
        ORDER BY period
    """).df()

    df_monthly_net_ex = conn.execute(f"""
        SELECT
            strftime(transaction_date, '%Y-%m') AS period,
            ROUND(SUM(amount), 2)               AS net_amount
        FROM transactions
        WHERE {savings_filter}
        GROUP BY period
        ORDER BY period
    """).df()

    # Net amount per quarter — format "24-1", "24-2" etc
    df_quarterly_net = conn.execute("""
        SELECT
            SUBSTR(CAST(year(transaction_date) AS VARCHAR), 3, 2)
                || '-' || CAST(quarter(transaction_date) AS VARCHAR) AS period,
            ROUND(SUM(amount), 2) AS net_amount
        FROM transactions
        GROUP BY period
        ORDER BY period
    """).df()

    df_quarterly_net_ex = conn.execute(f"""
        SELECT
            SUBSTR(CAST(year(transaction_date) AS VARCHAR), 3, 2)
                || '-' || CAST(quarter(transaction_date) AS VARCHAR) AS period,
            ROUND(SUM(amount), 2) AS net_amount
        FROM transactions
        WHERE {savings_filter}
        GROUP BY period
        ORDER BY period
    """).df()

    # Broad category totals and average per month
    df_broad = conn.execute(f"""
        SELECT
            {broad_col}                                                          AS broad,
            ROUND(SUM(amount), 2)                                                AS total_amount,
            ROUND(
                SUM(amount) / COUNT(DISTINCT strftime(transaction_date, '%Y-%m')),
                2
            )                                                                    AS avg_per_month
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
