#!/usr/bin/env python3
"""Load the transactions CSV into the dbt source database.

Usage:
    python3 dbt/load_source.py                          # DuckDB dev (default)
    python3 dbt/load_source.py --target prod            # BigQuery prod
    python3 dbt/load_source.py data/my_export.csv       # explicit CSV path
    python3 dbt/load_source.py data/my.csv --target prod
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.db import _build
from src import config

GCP_PROJECT = "spending-check-495420"
BQ_DATASET  = "spending_check"
BQ_TABLE    = "transactions"
DUCKDB_PATH = Path("spending_check.duckdb")


def load_duckdb(df) -> None:
    import duckdb
    file_conn = duckdb.connect(str(DUCKDB_PATH))
    file_conn.execute("DROP TABLE IF EXISTS transactions")
    file_conn.execute("CREATE TABLE transactions AS SELECT * FROM df")
    file_conn.close()
    print(f"Loaded {len(df):,} transactions → {DUCKDB_PATH}")


def load_bigquery(df) -> None:
    from google.cloud import bigquery

    client = bigquery.Client(project=GCP_PROJECT)
    table_id = f"{GCP_PROJECT}.{BQ_DATASET}.{BQ_TABLE}"

    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        autodetect=True,
    )
    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()
    print(f"Loaded {len(df):,} transactions → {table_id}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", nargs="?", help="Path to CSV file")
    parser.add_argument("--target", default="dev", choices=["dev", "prod"])
    args = parser.parse_args()

    csv = Path(args.csv) if args.csv else config.CSV_PATH
    if not csv.exists():
        print(f"CSV not found: {csv}", file=sys.stderr)
        sys.exit(1)

    mem_conn = _build(csv)
    df = mem_conn.execute("SELECT * FROM transactions").df()

    if args.target == "prod":
        load_bigquery(df)
    else:
        load_duckdb(df)


if __name__ == "__main__":
    main()
