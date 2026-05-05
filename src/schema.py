from __future__ import annotations

from pydantic import BaseModel, Field


class Insight(BaseModel):
    insight_type: str = Field(description="One of: monthly_summary, category_alert, recurring_alert, dormant_alert")
    headline: str = Field(description="Single sentence, plain English, no jargon")
    detail: str | None = Field(default=None, description="Optional supporting explanation, max 3 sentences")
    confidence: float = Field(ge=0.0, le=1.0, description="Model's confidence that this insight is meaningful")


class InsightReport(BaseModel):
    period_year: int
    period_month: int
    insights: list[Insight]


class CategorySpend(BaseModel):
    category: str
    total_spend: float
    transaction_count: int
    avg_transaction: float


class NetByPeriod(BaseModel):
    period: str
    net_amount: float


class BroadSummary(BaseModel):
    broad: str
    total_amount: float
    avg_per_month: float


class AnalyseResponse(BaseModel):
    period_year: int
    period_month: int
    insights: list[Insight]
    spend_by_category: list[CategorySpend]
    monthly_net: list[NetByPeriod]
    monthly_net_ex_savings: list[NetByPeriod]
    quarterly_net: list[NetByPeriod]
    quarterly_net_ex_savings: list[NetByPeriod]
    broad_summary: list[BroadSummary]
