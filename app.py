import streamlit as st
import pandas as pd
from dashboard.charts import (
    plot_top_products,
    plot_top_countries,
    plot_top_salespersons,
    plot_monthly_trends,
)
from dashboard.filters import country_filter, product_filter
from dashboard.utils import load_data

# Load data

df = load_data('data/Chocolate Sales (2).csv')

# Title
st.title("Chocolate Sales Dashboard")

# Filters
selected_country = country_filter(df)
selected_product = product_filter(df)

# Filtered data (keeps dashboard interactive)
filtered_df = df[
    (df['Country'] == selected_country) &
    (df['Product'] == selected_product)
]

# KPI uses the interactive filtered slice
st.metric("Total Sales", f"${filtered_df['Amount'].sum():,.2f}")

# Charts:
# - Product chart respects country selection (so it stays relevant)
# - Country & Salesperson charts use broader data to avoid over-filtering into a single category
product_df = df[df['Country'] == selected_country]

st.plotly_chart(plot_top_products(product_df))
st.plotly_chart(plot_top_countries(df))
st.plotly_chart(plot_top_salespersons(df))
st.plotly_chart(plot_monthly_trends(filtered_df))
