"""Thin wrapper around the Anthropic client — uses tool_use for guaranteed structured output."""
from __future__ import annotations

import logging

from src import config
from src.schema import InsightReport

logger = logging.getLogger(__name__)

_TOOL = {
    "name": "report_insights",
    "description": "Output spending insights as structured data.",
    "input_schema": {
        "type": "object",
        "properties": {
            "period_year": {"type": "integer"},
            "period_month": {"type": "integer"},
            "insights": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "insight_type": {
                            "type": "string",
                            "description": "One of: monthly_summary, category_alert, recurring_alert, dormant_alert",
                        },
                        "headline": {
                            "type": "string",
                            "description": "Single sentence, plain English",
                        },
                        "detail": {
                            "type": "string",
                            "description": "Optional supporting explanation, max 3 sentences",
                        },
                        "confidence": {
                            "type": "number",
                            "description": "0.0 to 1.0",
                        },
                    },
                    "required": ["insight_type", "headline", "confidence"],
                },
            },
        },
        "required": ["period_year", "period_month", "insights"],
    },
}


def get_insights(system_prompt: str, user_prompt: str, year: int, month: int) -> InsightReport:
    import anthropic

    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

    response = client.messages.create(
        model=config.ANTHROPIC_MODEL,
        max_tokens=2048,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
        tools=[_TOOL],
        tool_choice={"type": "tool", "name": "report_insights"},
    )

    usage = response.usage
    logger.info(
        "LLM call complete. Input tokens: %d, Output tokens: %d",
        usage.input_tokens,
        usage.output_tokens,
    )

    tool_block = next(b for b in response.content if b.type == "tool_use")
    data = tool_block.input
    data.setdefault("period_year", year)
    data.setdefault("period_month", month)

    return InsightReport.model_validate(data)
