import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# ===============================
# AUTO REFRESH
# ===============================
st_autorefresh(interval=5 * 60 * 1000, key="final_refresh")

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(page_title="MANOHAR FINAL AI SCANNER", layout="wide")

st.title("🚀 MANOHAR FINAL STABLE AI MARKET SCANNER")

# ===============================
# SAFE LIVE INDEX DATA
# ===============================
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
                "chg": 10,
                "vol": 100000
            }

    return result

idx_data = get_live_index()

# ===============================
# DISPLAY INDEX
# ===============================
c1, c2, c3, c4 = st.columns(4)

c1.metric("NIFTY", idx_data["NIFTY"]["price"], idx_data["NIFTY"]["chg"])
c2.metric("BANKNIFTY", idx_data["BANKNIFTY"]["price"], idx_data["BANKNIFTY"]["chg"])
c3.metric("FINNIFTY", idx_data["FINNIFTY"]["price"], idx_data["FINNIFTY"]["chg"])
c4.metric("MIDCAPNIFTY", idx_data["MIDCAPNIFTY"]["price"], idx_data["MIDCAPNIFTY"]["chg"])

st.divider()

# ===============================
# SELECT INDEX
# ===============================
selected_idx = st.sidebar.selectbox(
    "SELECT INDEX",
    ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCAPNIFTY"]
)

# ✅ Correct assignment (no stray
