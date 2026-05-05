"""Run the feature SQL files and return results as a typed dict."""
from __future__ import annotations

import logging

import pandas as pd

from src import config
from src.db import run_sql_file

logger = logging.getLogger(__name__)

_FEATURES_DIR = config.SQL_DIR / "features"


def monthly_by_category(year: int, month: int) -> pd.DataFrame:
    return run_sql_file(
        _FEATURES_DIR / "monthly_by_category.sql",
        {"year": year, "month": month},
    )


def category_trend(months: int = 6) -> pd.DataFrame:
    return run_sql_file(
        _FEATURES_DIR / "category_trend.sql",
        {"months": months},
    )


def recurring_merchants(min_months: int = 3, lookback_months: int = 6) -> pd.DataFrame:
    return run_sql_file(
        _FEATURES_DIR / "recurring_merchants.sql",
        {"min_months": min_months, "lookback_months": lookback_months},
    )


def dormant_subscriptions(gap_months: int = 2, lookback_months: int = 12) -> pd.DataFrame:
    return run_sql_file(
        _FEATURES_DIR / "dormant_subscriptions.sql",
        {"gap_months": gap_months, "lookback_months": lookback_months},
    )


def collect_all(year: int, month: int) -> dict[str, pd.DataFrame]:
    logger.info("Collecting features...")
    return {
        "monthly_by_category": monthly_by_category(year, month),
        "category_trend": category_trend(),
        "recurring_merchants": recurring_merchants(),
        "dormant_subscriptions": dormant_subscriptions(),
    }
