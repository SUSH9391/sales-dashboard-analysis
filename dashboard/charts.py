import plotly.express as px
import pandas as pd

def plot_top_products(df):
    top_products = (
        df.groupby('Product')['Amount']
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    fig = px.bar(
        top_products,
        x='Amount',
        y='Product',
        orientation='h',
        title='Top 10 Products by Sales'
    )
    return fig

def plot_monthly_trends(df):
    # Assumes df['Date'] is already parsed in utils.load_data()
    monthly_df = df.copy()
    monthly_df['Month'] = monthly_df['Date'].dt.to_period('M')
    monthly_sales = monthly_df.groupby('Month')['Amount'].sum()
    fig = px.line(
        x=monthly_sales.index.astype(str),
        y=monthly_sales.values,
        markers=True,
        title='Monthly Sales Trends'
    )
    return fig

def plot_top_countries(df):
    top_countries = (
        df.groupby('Country')['Amount']
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    fig = px.bar(
        top_countries,
        x='Amount',
        y='Country',
        orientation='h',
        title='Top 10 Countries by Sales',
    )
    return fig

def plot_top_salespersons(df):
    top_salespersons = (
        df.groupby('Sales Person')['Amount']
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    fig = px.bar(
        top_salespersons,
        x='Amount',
        y='Sales Person',
        orientation='h',
        title='Top 10 Salespersons by Sales',
    )
    return fig
