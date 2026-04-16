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
# 2. RSI CALCULATION (Manual)
# =============================
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# =============================
# 3. SuperTrend Calculation
# =============================
def calculate_supertrend(df, period=10, multiplier=3):
    hl2 = (df['High'] + df['Low']) / 2
    atr = df['High'].rolling(period).max() - df['Low'].rolling(period).min()
    upperband = hl2 + (multiplier * atr)
    lowerband = hl2 - (multiplier * atr)
    supertrend = pd.Series(index=df.index, dtype=float)

    # Simple logic: if close > upperband → Bullish, else Bearish
    for i in range(len(df)):
        if df['Close'].iloc[i] > upperband.iloc[i]:
            supertrend.iloc[i] = 1
        elif
