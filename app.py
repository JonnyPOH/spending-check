import tempfile
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="Spending Check", page_icon="💷", layout="centered")
st.title("💷 Spending Check")

uploaded = st.file_uploader("Upload your transactions CSV", type=["csv"])

if uploaded:
    # Only reload the DB when a new file is uploaded
    if st.session_state.get("loaded_file") != uploaded.name:
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            f.write(uploaded.getvalue())
            tmp_path = Path(f.name)
        from src.db import reset
        reset(tmp_path)
        st.session_state.loaded_file = uploaded.name
        st.session_state.pop("report", None)

    from src.pipeline import _last_complete_month
    default_year, default_month = _last_complete_month()

    col1, col2 = st.columns(2)
    year = col1.number_input("Year", value=default_year, min_value=2000, max_value=2030, step=1)
    month = col2.number_input("Month", value=default_month, min_value=1, max_value=12, step=1)

    if st.button("Analyse", type="primary"):
        with st.spinner("Analysing your spending..."):
            from src.features import monthly_by_category
            from src.pipeline import run
            report = run(year=int(year), month=int(month))
            df_chart = monthly_by_category(int(year), int(month))
        st.session_state.report = report
        st.session_state.df_chart = df_chart

    if "report" in st.session_state:
        report = st.session_state.report
        df_chart = st.session_state.df_chart

        if not df_chart.empty:
            st.subheader("Spend by category")
            st.bar_chart(df_chart.set_index("category")["total_spend"])

        st.subheader("Insights")
        for insight in report.insights:
            with st.container(border=True):
                st.markdown(f"**{insight.headline}**")
                if insight.detail:
                    st.write(insight.detail)
                st.caption(f"{insight.insight_type} · {insight.confidence:.0%} confidence")
