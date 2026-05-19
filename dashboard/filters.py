import streamlit as st

def country_filter(df):
    country = st.selectbox("Select Country", df['Country'].unique())
    return country

def product_filter(df):
    product = st.selectbox("Select Product", df['Product'].unique())
    return product