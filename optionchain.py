import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# ==========================================
# AUTO REFRESH
# ==========================================
st_autorefresh(interval=5 * 60 * 1000, key="stable_refresh")

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(page_title="MANOHAR STABLE AI SCANNER", layout="wide")

st.title("🚀 MANOHAR STABLE AI MARKET SCANNER")

# ==========================================
# SAFE LIVE INDEX DATA (NEVER FAIL)
# ==========================================
def get_live_index():
    symbols = {
        "NIFTY": "^NSEI",
        "BANKNIFTY": "^NSEBANK",
        "FINNIFTY": "^NSEI",
        "MIDCAPNIFTY": "^NSEI"
    }

    result = {}

    for name, symbol in symbols.items():
        try:
            data = yf.Ticker(symbol).history(period="1d", interval="5m")

            if data.empty:
                raise Exception("No data")

            last = data.iloc[-1]
            prev = data.iloc[-2]

            result[name] = {
                "price": round(last["Close"], 2),
                "chg": round(last["
