from __future__ import annotations

import pandas as pd

SYSTEM = """\
You are a sharp personal finance analyst reviewing one person's real bank transactions. \
Your job is to surface insights that are genuinely useful — things the person might not \
have noticed themselves.

Rules:
- Always compare the target month to the prior months where data is available
- Name specific amounts, categories, and merchants — never be vague
- Flag anomalies: anything unusually high, unusually low, or out of pattern
- Identify recurring charges the person may have forgotten about
- Highlight positive trends as well as areas of concern
- Never hallucinate figures — only state what the data shows
- If confidence is below 0.6, still include the insight but flag the uncertainty
- Aim for 4–6 insights, ordered by importance"""


def build_user_prompt(features: dict[str, pd.DataFrame], year: int, month: int) -> str:
    def df_to_text(df: pd.DataFrame) -> str:
        return df.to_string(index=False) if not df.empty else "(no data)"

    sections = "\n\n".join(
        f"## {name.replace('_', ' ').title()}\n{df_to_text(df)}"
        for name, df in features.items()
    )

    return f"""\
Target month: {year}-{month:02d}

The data below covers the target month plus up to 6 months of history. \
Use the historical context to identify trends, anomalies, and changes in behaviour. \
Focus on what's actionable — what should this person pay attention to or do differently?

{sections}"""
