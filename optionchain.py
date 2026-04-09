import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="🔥 Option Chain Ultimate", layout="wide")
st.title("📊 Option Chain Smart Scanner")

# =============================
# SIDEBAR (INDEX + SEARCH)
# =============================
st.sidebar.title("📊 Market Setup")

indices = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"]
index_symbol = st.sidebar.selectbox("Select Index", indices)

expiry_type = st.sidebar.selectbox("Select Expiry", ["Weekly", "Monthly"])

st.sidebar.subheader("🔍 Search Stock")
search_stock = st.sidebar.text_input("Enter Stock (Ex: RELIANCE)")

# Decide Symbol
if search_stock.strip() != "":
    symbol = search_stock.upper()
    market_type = "Stock"
else:
    symbol = index_symbol
    market_type = "Index"

# =============================
# FETCH DATA
# =============================
def fetch_data():
    try:
        if market_type == "Index":
            url = f"https://api.allorigins.win/raw?url=https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
        else:
            url = f"https://api.allorigins.win/raw?url=https://www.nseindia.com/api/option-chain-equities?symbol={symbol}"

        res = requests.get(url, timeout=10)

        if res.status_code != 200:
            return None

        data = res.json()

        if "records" not in data:
            return None

        rows = []
        for item in data["records"]["data"]:
            rows.append({
                "Strike": item.get("strikePrice", 0),
                "Call_OI": item.get("CE
