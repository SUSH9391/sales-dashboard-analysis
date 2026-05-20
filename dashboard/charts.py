import plotly.express as px
import pandas as pd


def _apply_common_hover(fig):
    # Premium-ish baseline: cleaner legend + consistent hover formatting.
    fig.update_layout(legend_title_text="")
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=50, b=10),
    )
    return fig


def plot_top_products(df):
    top_products = (
        df.groupby("Product")["Amount"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    fig = px.bar(
        top_products,
        x="Amount",
        y="Product",
        orientation="h",
        title="Top 10 Products by Sales",
    )
    fig.update_traces(
        hovertemplate="<b>%{y}</b><br>Sales: $%{x:,.2f}<extra></extra>"
    )
    return _apply_common_hover(fig)


def plot_monthly_trends(df):
    # Assumes df['Date'] is already parsed in utils.load_data()
    monthly_df = df.copy()
    monthly_df["Month"] = monthly_df["Date"].dt.to_period("M")
    monthly_sales = monthly_df.groupby("Month")["Amount"].sum()
    fig = px.line(
        x=monthly_sales.index.astype(str),
        y=monthly_sales.values,
        markers=True,
        title="Monthly Sales Trends",
    )
    fig.update_traces(hovertemplate="<b>%{x}</b><br>Sales: $%{y:,.2f}<extra></extra>")
    return _apply_common_hover(fig)


def plot_top_countries(df):
    top_countries = (
        df.groupby("Country")["Amount"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    fig = px.bar(
        top_countries,
        x="Amount",
        y="Country",
        orientation="h",
        title="Top 10 Countries by Sales",
    )
    fig.update_traces(hovertemplate="<b>%{y}</b><br>Sales: $%{x:,.2f}<extra></extra>")
    return _apply_common_hover(fig)


def plot_top_salespersons(df):
    top_salespersons = (
        df.groupby("Sales Person")["Amount"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    fig = px.bar(
        top_salespersons,
        x="Amount",
        y="Sales Person",
        orientation="h",
        title="Top 10 Salespersons by Sales",
    )
    fig.update_traces(hovertemplate="<b>%{y}</b><br>Sales: $%{x:,.2f}<extra></extra>")
    return _apply_common_hover(fig)

