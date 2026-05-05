# Spending Insights

A personal finance analytics pipeline that pulls structured features from a SQL Server database, sends them to Claude, and writes structured insights back to SQL — on a monthly schedule via GitHub Actions.

```
transactions (SQL Server)
        │
        ▼
   Feature queries (4× .sql files)
        │
        ▼
  Claude (claude-sonnet-4-6)
        │
        ▼
  Structured output (Pydantic → JSON)
        │
        ▼
  insights table (SQL Server)
```

## Features extracted

| Feature | What it answers |
|---|---|
| `monthly_by_category` | Where did the money go this month? |
| `category_trend` | Which categories are trending up or down? |
| `recurring_merchants` | What subscriptions am I paying? |
| `dormant_subscriptions` | What did I forget to cancel? |

## Stack

- **SQL Server 2022** (Docker) — transaction storage and feature computation
- **Python 3.12** — pipeline orchestration
- **Anthropic Claude** — insight generation with structured JSON output
- **Pydantic v2** — output schema validation
- **GitHub Actions** — monthly cron deployment

## Quick start

```bash
# 1. Clone and install
git clone <repo>
cd spending-insights
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Configure secrets
cp .env.example .env
# Edit .env — add ANTHROPIC_API_KEY and optionally adjust MSSQL_PASSWORD

# 3. Start SQL Server
make db-up

# 4. Initialise schema and load sample data
python -m src.db --init --seed

# 5. Run the pipeline
make pipeline
```

## Running with your own data

Place your CSV at `data/transactions_real.csv` (gitignored) with columns:

```
transaction_date, description, amount, category, merchant, account, currency
```

Then set `CSV_PATH=data/transactions_real.csv` in `.env` and run `make seed`.

## Tests

```bash
make test                     # all tests (DB tests skipped unless SQL Server is up)
SKIP_DB_TESTS=1 pytest tests/ # schema + smoke tests only, no DB required
```

## Eval harness

```bash
make eval
```

Generates synthetic data with planted patterns (double charge, dormant subscription, spend spike), runs the full pipeline, and reports what percentage of planted truths were recalled.

## Deployment

Add these secrets to your GitHub repo (Settings → Secrets → Actions):

- `ANTHROPIC_API_KEY`
- `MSSQL_PASSWORD`

The workflow in `.github/workflows/monthly_run.yml` runs on the 1st of each month.
