import plotly.express as px
import pandas as pd

def plot_top_products(df):
    top_products = df.groupby('Product')['Amount'].sum().sort_values(ascending=False)
    fig = px.bar(
        x=top_products.head(10).values, 
        y=top_products.head(10).index,
        orientation='h',
        title='Top 10 Products by Sales'
    )
    return fig

def plot_monthly_trends(df):
    df['Date'] = pd.to_datetime(df['Date'])
    df['Month'] = df['Date'].dt.to_period('M')
    monthly_sales = df.groupby('Month')['Amount'].sum()
    fig = px.line(
        x=monthly_sales.index.astype(str), 
        y=monthly_sales.values,
        markers=True,
        title='Monthly Sales Trends'
    )
    return fig