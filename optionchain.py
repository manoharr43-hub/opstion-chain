import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf

st.set_page_config(page_title="🔥 NSE AI Smart Money Scanner", layout="wide")

# =========================
# DATA LOADER
# =========================
@st.cache_data
def load_data(symbol="^NSEI", period="5d", interval="5m"):
    df = yf.download(symbol, period=period, interval=interval)
    df.dropna(inplace=True)
    return df

# =========================
# SMART MONEY LOGIC (FIXED)
# =========================
def smart_money(df):
    df = df.copy()

    df["change"] = df["Close"] - df["Open"]
    df["volume_change"] = df["Volume"].diff().fillna(0)

    # SAFE scalar calculations (NO Series error)
    bullish_volume = df.loc[df["change"] > 0, "Volume"].sum()
    bearish_volume = df.loc[df["change"] < 0, "Volume"].sum()

    total_change = df["change"].sum()

    if total_change > 0:
        trend = "🟢 BULLISH"
    else:
        trend = "🔴 BEARISH"

    return bullish_volume, bearish_volume, trend

# =========================
# BIG MOVERS
# =========================
def detect_big_moves(df, threshold=0.3):
    df = df.copy()
    df["pct_change"] = df["Close"].pct_change() * 100

    big_moves = df[abs(df["pct_change"]) > threshold].copy()
    return big_moves

# =========================
# STREAMLIT UI
# =========================
st.title("🔥 NSE AI Smart Money + Big Movers Scanner")

symbol = st.text_input("Enter Symbol", "^NSEI")

df = load_data(symbol)

st.subheader("📊 Live Chart Data")
st.dataframe(df.tail(20))

# =========================
# SMART MONEY OUTPUT
# =========================
bullish, bearish, trend = smart_money(df)

st.subheader("🧠 Smart Money Analysis")
st.write("Bullish Volume:", bullish)
st.write("Bearish Volume:", bearish)
st.success(f"Market Trend: {trend}")

# =========================
# BIG MOVERS
# =========================
st.subheader("⚡ Big Movers Detection")
big_moves = detect_big_moves(df)

if not big_moves.empty:
    st.dataframe(big_moves.tail(20))
else:
    st.warning("No big moves detected now")

# =========================
# SIMPLE SIGNAL
# =========================
last = df.iloc[-1]

if last["Close"] > last["Open"]:
    st.success("📈 BUY Pressure Detected")
else:
    st.error("📉 SELL Pressure Detected")
