import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

st.title("📊 NSE Option Chain + Intraday Dashboard")

# Example ticker
bt_date = datetime(2026, 4, 16)  # backtest date
t = yf.Ticker("TATAMOTORS.NS")

# Fetch intraday history
df_hist = t.history(start=bt_date, end=bt_date + timedelta(days=1), interval="5m")
df_hist = df_hist.between_time("09:15", "15:30")

# Display safely
st.dataframe(df_hist, width="stretch")
