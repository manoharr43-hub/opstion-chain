import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# =============================
# 1. CONFIG
# =============================
st.set_page_config(page_title="🔥 MANOHAR NSE AI PRO", layout="wide")
st_autorefresh(interval=60000, key="refresh")

st.title("🚀 MANOHAR NSE AI PRO TERMINAL")
st.markdown("---")

# =============================
# 2. ANALYSIS LOGIC (SAFE + OLD SAFE)
# =============================
def analyze_data(df):
    try:
        if df is None or df.empty or len(df) < 20:
            return None

        # EMA
        e20 = df['Close'].ewm(span=20).mean()
        e50 = df['Close'].ewm(span=50).mean()

        # Volume
        vol = df['Volume']
        avg_vol = vol.rolling(window=20).mean()

        curr_price = df['Close'].iloc[-1]
        curr_e20 = e20.iloc[-1]
        curr_e50 = e50.iloc[-1]
        curr_vol = vol.iloc[-1]
        curr_avg_vol = avg_vol.iloc[-1]

        # SAFE CHECK (NaN protection)
        if pd.isna(curr_avg_vol) or pd.isna(curr_e20) or pd.isna(curr_e50):
            return None

        # =============================
        # TREND
        # =============================
        cp_strength = "🔵 CALL STRONG" if curr_e20 > curr_e50 else "🔴 PUT STR
