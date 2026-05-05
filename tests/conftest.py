import duckdb
import pandas as pd
import pytest

import src.db as db_module

_SAMPLE = pd.DataFrame({
    "transaction_date": pd.to_datetime([
        "2025-11-01", "2025-11-15",
        "2025-12-01", "2025-12-15",
        "2026-01-01", "2026-01-15",
        "2026-02-01", "2026-02-15",
        "2026-03-01", "2026-03-15",
    ]),
    "description": ["Spotify", "Tesco"] * 5,
    "amount": [-9.99, -55.0] * 5,
    "category": ["Subscriptions", "Groceries"] * 5,
    "merchant": ["Spotify", "Tesco"] * 5,
    "account": ["Current"] * 10,
    "currency": ["GBP"] * 10,
})


@pytest.fixture(autouse=True)
def inject_test_db(monkeypatch):
    conn = duckdb.connect()
    conn.register("transactions", _SAMPLE)
    monkeypatch.setattr(db_module, "_conn", conn)
    yield
    monkeypatch.setattr(db_module, "_conn", None)
