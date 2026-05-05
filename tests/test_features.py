import pandas as pd


def test_monthly_by_category_shape():
    from src.features import monthly_by_category

    df = monthly_by_category(2026, 1)
    assert isinstance(df, pd.DataFrame)
    assert set(df.columns) >= {"category", "total_spend", "transaction_count", "avg_transaction"}


def test_category_trend_shape():
    from src.features import category_trend

    df = category_trend(months=6)
    assert isinstance(df, pd.DataFrame)
    assert "year_month" in df.columns
    assert "pct_change" in df.columns


def test_recurring_merchants_shape():
    from src.features import recurring_merchants

    df = recurring_merchants()
    assert isinstance(df, pd.DataFrame)
    assert "merchant" in df.columns
    assert "avg_monthly_spend" in df.columns


def test_dormant_subscriptions_shape():
    from src.features import dormant_subscriptions

    df = dormant_subscriptions()
    assert isinstance(df, pd.DataFrame)
    assert "last_transaction_date" in df.columns
