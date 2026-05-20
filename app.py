import streamlit as st

from dashboard.charts import (
    plot_top_products,
    plot_top_countries,
    plot_top_salespersons,
    plot_monthly_trends,
)
from dashboard.filters import country_filter, product_filter
from dashboard.utils import load_data
from dashboard.insights import generate_key_insights
from dashboard.forecast import forecast_monthly_sales
from dashboard.metrics import compute_real_world_kpis


def _apply_theme(theme: str) -> None:
    if theme == "Dark":
        st.set_page_config(
            page_title="Chocolate Sales Dashboard",
            layout="wide",
            initial_sidebar_state="expanded",
        )
        st.markdown(
            """
            <style>
            body { background-color: #0b0f19; }
            .stApp { color: #e8edf6; }
            .metric-card { background: rgba(255,255,255,0.04); border-radius: 12px; padding: 12px; }
            </style>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.set_page_config(
            page_title="Chocolate Sales Dashboard",
            layout="wide",
            initial_sidebar_state="expanded",
        )


# Load data
df = load_data("data/Chocolate Sales (2).csv")

# Theme toggle
theme = st.sidebar.radio("Theme", ["Light", "Dark"], index=1)
_apply_theme(theme)

st.title("Chocolate Sales Dashboard")

# Filters
selected_country = country_filter(df)
selected_product = product_filter(df)

filtered_df = df[(df["Country"] == selected_country) & (df["Product"] == selected_product)]

# Layout: premium cards via columns + tabs
kpi1, kpi2, kpi3 = st.columns(3)

kpi_total_sales = float(filtered_df["Amount"].sum())
kpi1.metric("Total Sales", f"${kpi_total_sales:,.2f}")

# Secondary KPIs (may be N/A)
kpi_data = compute_real_world_kpis(filtered_df)
profit_margin = next((k["value"] for k in kpi_data["kpis"] if k["name"] == "Profit margin"), "N/A")
retention_proxy = next(
    (k["value"] for k in kpi_data["kpis"] if k["name"] == "Retention rate (proxy)"), "N/A"
)

kpi2.metric("Profit margin", profit_margin)
kpi3.metric("Retention rate", retention_proxy)

# Tabs
overview_tab, insights_tab, forecast_tab, details_tab = st.tabs(
    ["Overview", "Key Insights", "Forecast", "Explain Decisions"]
)

with overview_tab:
    st.subheader("Performance at a glance")

    product_df = df[df["Country"] == selected_country]

    st.plotly_chart(plot_top_products(product_df), use_container_width=True)
    st.plotly_chart(plot_top_countries(df), use_container_width=True)
    st.plotly_chart(plot_top_salespersons(df), use_container_width=True)
    st.plotly_chart(plot_monthly_trends(filtered_df), use_container_width=True)

with insights_tab:
    st.subheader("Key Insights")

    insights = generate_key_insights(filtered_df)
    for block in insights:
        st.markdown(f"### {block['title']}")
        for b in block["bullets"]:
            st.write(f"• {b}")

with forecast_tab:
    st.subheader("Forecasting (baseline)")
    hist, forecast, fig = forecast_monthly_sales(filtered_df, periods=3)

    if fig is None:
        st.info("Not enough monthly history to forecast.")
    else:
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Baseline model: rolling-mean + simple recent delta extrapolation.")

with details_tab:
    st.subheader("Why I chose these KPIs")
    st.write(
        "KPIs combine revenue impact (Total Sales), unit economics proxy (Profit margin when available), and customer stability (Retention proxy). "
        "When full columns are missing in the dataset, the dashboard explicitly switches to safe proxies and labels them as such."
    )

    st.subheader("Challenges faced")
    st.write(
        "- Dataset is limited in columns for true CLV/Retention/margin in some slices.\n"
        "- Date parsing requires robust handling of mixed formats.\n"
        "- Narrative insights must be deterministic and not hallucinate missing fields."
    )

    st.subheader("Optimization done")
    st.write(
        "- Insights + metrics are filter-aware (use the interactive slice).\n"
        "- Forecasting uses a lightweight baseline that won’t break with small datasets.\n"
        "- Plot hovers and layout are cleaned for a more premium BI feel."
    )

    st.subheader("Business value")
    st.write(
        "This dashboard helps quickly answer: what changed, where it comes from (product/country/month signals), and what to expect next month — enabling faster prioritization in merchandising and sales planning."
    )

    st.subheader("Real-world metrics (computed where possible)")
    for k in kpi_data["kpis"]:
        st.write(f"**{k['name']}**: {k['value']} — {k['explanation']}")
    for n in kpi_data.get("notes", []):
        st.info(n)

