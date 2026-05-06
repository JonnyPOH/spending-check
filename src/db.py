"""DuckDB in-memory query engine — loads CSV once, runs SQL feature files."""
from __future__ import annotations

import logging
from pathlib import Path

import duckdb
import pandas as pd

from src import config

logger = logging.getLogger(__name__)

_COLUMN_ALIASES = {
    "date": "transaction_date",
    "amount (£)": "amount",
    "amount(£)": "amount",
}

_conn: duckdb.DuckDBPyConnection | None = None


def _get_connection() -> duckdb.DuckDBPyConnection:
    global _conn
    if _conn is None:
        _conn = _build(config.CSV_PATH)
    return _conn


def _build(csv_path: Path) -> duckdb.DuckDBPyConnection:
    df = pd.read_csv(csv_path, encoding="latin-1")
    df.columns = [c.strip().lower() for c in df.columns]
    df.rename(columns=_COLUMN_ALIASES, inplace=True)

    expected = {"transaction_date", "description", "amount", "category"}
    missing = expected - set(df.columns)
    if missing:
        raise ValueError(f"CSV is missing required columns: {missing}")

    col = df["transaction_date"]
    if pd.api.types.is_numeric_dtype(col):
        # Excel date serial: days since 1899-12-30
        df["transaction_date"] = pd.to_datetime(col, unit="D", origin="1899-12-30")
    else:
        df["transaction_date"] = pd.to_datetime(col, dayfirst=True)

    for col in ("merchant", "account"):
        if col not in df.columns:
            df[col] = None
    if "currency" not in df.columns:
        df["currency"] = "GBP"

    conn = duckdb.connect()
    conn.register("transactions", df)
    logger.info("Loaded %d transactions from %s", len(df), csv_path)
    return conn


def reset(csv_path: Path) -> None:
    """Load a new CSV, replacing any existing connection."""
    global _conn
    _conn = _build(csv_path)


def reset_from_df(df: "pd.DataFrame") -> None:
    """Load from a pre-normalised DataFrame (e.g. from TrueLayer)."""
    global _conn
    import pandas as pd  # noqa: F401 — ensure type is resolved
    conn = duckdb.connect()
    conn.register("transactions", df)
    _conn = conn
    logger.info("Loaded %d transactions from DataFrame", len(df))


def run_sql_file(path: Path, params: dict | None = None) -> pd.DataFrame:
    """Execute a .sql file against the in-memory transactions table."""
    sql = path.read_text(encoding="utf-8")
    if params:
        for key, value in params.items():
            sql = sql.replace(f":{key}", str(value))
    return _get_connection().execute(sql).df()
