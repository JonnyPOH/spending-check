import pytest
from pydantic import ValidationError

from src.schema import Insight, InsightReport


def test_insight_valid():
    i = Insight(insight_type="monthly_summary", headline="You spent more on eating out.", confidence=0.9)
    assert i.confidence == 0.9
    assert i.detail is None


def test_insight_confidence_bounds():
    with pytest.raises(ValidationError):
        Insight(insight_type="x", headline="x", confidence=1.5)
    with pytest.raises(ValidationError):
        Insight(insight_type="x", headline="x", confidence=-0.1)


def test_report_valid():
    report = InsightReport(
        period_year=2025,
        period_month=1,
        insights=[
            Insight(insight_type="monthly_summary", headline="Low spend month.", confidence=0.8)
        ],
    )
    assert len(report.insights) == 1
    assert report.period_month == 1


def test_report_empty_insights():
    report = InsightReport(period_year=2025, period_month=3, insights=[])
    assert report.insights == []
