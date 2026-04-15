import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# =============================
# CONFIG
# =============================
st.set_page_config(page_title="🔥 NSE AI DEBUG TERMINAL", layout="wide")
st_autorefresh(interval=60000, key="refresh")

st.title("🧪 NSE AI DEBUG MODE TERMINAL")
st.markdown("---")

# =============================
# DEBUG LOG CONTAINER
# =============================
log_box = st.empty()

def log(msg):
    log_box.text(msg)

# =============================
# SAFE ANALYSIS
# =============================
def analyze_data(df):
    if df is None or df.empty:
        return None

    if len(df) < 20:
        return None

    df = df.copy()

    df["EMA20"] = df["Close"].ewm(span=20).mean()
    df["EMA50"] = df["Close"].ewm(span=50).mean()
    df["VOL_AVG"] = df["Volume"].rolling(20).mean()

    curr_price = df["Close"].iloc[-1]
    curr_e20 = df["EMA20"].iloc[-1]
    curr_e50 = df["EMA50"].iloc[-1]
    curr_vol = df["Volume"].iloc[-1]
    curr_avg_vol = df["VOL_AVG"].iloc[-1]

    if np.isnan(curr_avg_vol):
        return None

    signal = "WAIT"
    entry = sl = target = 0

    recent_high = df["High"].iloc[-10:].max()
    recent_low = df["Low"].iloc[-10:].min()
    risk = max((recent_high - recent_low), curr_price * 0.01)

    if curr_e20 > curr_e50 and curr_vol > curr_avg_vol:
        signal = "BUY"
        entry = curr_price
        sl = curr_price - risk * 0.5
        target = curr_price + risk

    elif curr_e20 < curr_e50 and curr_vol > curr_avg_vol:
        signal = "SELL"
        entry = curr_price
        sl = curr_price + risk * 0.5
        target = curr_price - risk

    return signal, round(entry, 2), round(sl, 2), round(target, 2)

# =============================
# STOCK LIST
# =============================
stocks = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN"]

# =============================
# DEBUG SCANNER
# =============================
if st.button("🧪 RUN DEBUG SCANNER"):

    results = []
    debug_logs = []

    for s in stocks:
        try
