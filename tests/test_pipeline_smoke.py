"""Smoke test: full pipeline with mocked LLM and mocked DB features."""

from unittest.mock import patch

import pandas as pd
import src.pipeline  # must be imported before @patch resolves the target

from src.schema import Insight, InsightReport


def _mock_features():
    return {
        "monthly_by_category": pd.DataFrame(
            {"category": ["Food"], "total_spend": [200.0], "transaction_count": [10], "avg_transaction": [20.0]}
        ),
        "category_trend": pd.DataFrame(
            {"year_month": ["2025-01"], "category": ["Food"], "total_spend": [200.0], "prev_month_spend": [180.0], "pct_change": [11.1]}
        ),
        "recurring_merchants": pd.DataFrame(
            {"merchant": ["Netflix"], "months_active": [6], "avg_monthly_spend": [10.99], "stdev_spend": [0.0], "coefficient_of_variation": [0.0]}
        ),
        "dormant_subscriptions": pd.DataFrame(columns=["merchant", "months_active", "last_transaction_date", "months_since_last"]),
    }


def _mock_report():
    return InsightReport(
        period_year=2025,
        period_month=1,
        insights=[
            Insight(insight_type="monthly_summary", headline="Food spend up 11% vs last month.", confidence=0.85)
        ],
    )


@patch("src.pipeline.get_insights", return_value=_mock_report())
@patch("src.pipeline.collect_all", return_value=_mock_features())
def test_pipeline_smoke(mock_features, mock_llm):
    from src.pipeline import run

    report = run(year=2025, month=1)

    mock_features.assert_called_once()
    mock_llm.assert_called_once()

    assert len(report.insights) == 1
    assert report.insights[0].confidence == 0.85
