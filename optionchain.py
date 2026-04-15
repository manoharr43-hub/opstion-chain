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
# 2. ANALYSIS LOGIC (SAFE + OLD LOGIC SAME)
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

        # SAFE CHECK
        if pd.isna(curr_e20) or pd.isna(curr_e50) or pd.isna(curr_avg_vol):
            return None

        # =============================
        # TREND (FIXED ERROR SAFE)
        # =============================
        if curr_e20 > curr_e50:
            cp_strength = "🔵 CALL STRONG"
        else:
            cp_strength = "🔴 PUT STRONG"

        # =============================
        # BIG PLAYER (2 LEVEL ONLY)
        # =============================
        if curr_vol > curr_avg_vol * 1.5:
            big_player = "🐋 BIG PLAYER ACTIVE"
        else:
            big_player = "💤 NORMAL"

        # DEFAULT
        observation = "WAIT"
        entry, sl, target = 0, 0, 0

        # RISK
        recent_high = df['High'].iloc[-10:].max()
        recent_low = df['Low'].iloc[-10:].min()

        risk = recent_high - recent_low
        if risk <= 0:
            risk = curr_price * 0.01

        # =============================
        # SIGNAL LOGIC (OLD SAFE)
        # =============================
        if curr_e20 > curr_e50 and curr_vol > curr_avg_vol:
            observation = "🚀 STRONG BUY"
            entry = curr_price
            sl = curr_price - (risk *
