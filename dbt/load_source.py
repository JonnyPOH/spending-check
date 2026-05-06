#!/usr/bin/env python3
"""Load the transactions CSV into spending_check.duckdb so dbt can run against it.

Usage:
    python dbt/load_source.py                         # uses default CSV_PATH from .env
    python dbt/load_source.py data/my_export.csv      # explicit path
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import duckdb
from src.db import _build

DB_PATH = Path("spending_check.duckdb")


def main() -> None:
    from src import config
    csv = Path(sys.argv[1]) if len(sys.argv) > 1 else config.CSV_PATH
    if not csv.exists():
        print(f"CSV not found: {csv}", file=sys.stderr)
        sys.exit(1)

    mem_conn = _build(csv)
    df = mem_conn.execute("SELECT * FROM transactions").df()

    file_conn = duckdb.connect(str(DB_PATH))
    file_conn.execute("DROP TABLE IF EXISTS transactions")
    file_conn.execute("CREATE TABLE transactions AS SELECT * FROM df")
    file_conn.close()

    print(f"Loaded {len(df):,} transactions → {DB_PATH}")


if __name__ == "__main__":
    main()
