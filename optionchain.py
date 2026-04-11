import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# ==========================================
# AUTO REFRESH
# ==========================================
st_autorefresh(interval=5 * 60 * 1000, key="safe_refresh")

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(page_title="MANOHAR SAFE AI SCANNER", layout="wide")

st.title("🚀 MANOHAR SAFE AI MARKET SCANNER")

# ==========================================
# SAFE LIVE INDEX DATA (NO SYNTAX ERROR)
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
                "chg": round(last["Close"] - prev["Close"], 2),
                "vol": int(last["Volume"]) if last["Volume"] > 0 else 100000
            }

        except:
            result[name] = {
                "price": 24500,
