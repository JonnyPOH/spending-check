"""Main pipeline: CSV → SQL features → LLM → printed insights."""
from __future__ import annotations

import datetime
import logging

from src import config
from src.db import _get_connection
from src.features import collect_all
from src.llm import get_insights
from src.prompts import SYSTEM, build_user_prompt
from src.schema import InsightReport

logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)

# logic for finding the last complete month
def _last_complete_month() -> tuple[int, int]:
    today = datetime.date.today()
    row = _get_connection().execute(
        "SELECT MAX(transaction_date)::DATE FROM transactions"
    ).fetchone()
    if row and row[0]:
        latest = row[0]
        if latest.year == today.year and latest.month == today.month:
            prev = today.replace(day=1) - datetime.timedelta(days=1)
            return prev.year, prev.month
        return latest.year, latest.month
    prev = today.replace(day=1) - datetime.timedelta(days=1)
    return prev.year, prev.month



def run(year: int | None = None, month: int | None = None) -> InsightReport:
    if year is None or month is None:
        year, month = _last_complete_month()

    logger.info("Running pipeline for %d-%02d", year, month)

    features = collect_all(year, month)
    user_prompt = build_user_prompt(features, year, month)
    report = get_insights(SYSTEM, user_prompt, year, month)

    print(f"\n=== Insights for {report.period_year}-{report.period_month:02d} ===\n")
    for i, insight in enumerate(report.insights, 1):
        print(f"{i}. [{insight.insight_type}] {insight.headline}")
        if insight.detail:
            print(f"   {insight.detail}")
        print(f"   confidence: {insight.confidence:.0%}\n")

    return report


if __name__ == "__main__":
    run()
