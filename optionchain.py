import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf

st.set_page_config(page_title="🔥 NSE AI Smart Trader (NEW)", layout="wide")

# =========================
# DATA LOADER
# =========================
def load_data(symbol="^NSEI"):
    df = yf.download(symbol, period="5d", interval="5m")
    df = df.dropna().copy()
    return df

# =========================
# SMART MONEY ENGINE
# =========================
def smart_money_engine(df):
    df = df.copy()

    df["change"] = df["Close"] - df["Open"]

    bullish_vol = df.loc[df["change"] > 0, "Volume"].sum()
    bearish_vol = df.loc[df["change"] < 0, "Volume"].sum()

    total_change = df["change"].sum()

    trend = "🟢 BULLISH" if total_change > 0 else "🔴 BEARISH"

    return bullish_vol, bearish_vol, trend

# =========================
# SIGNAL ENGINE (SAFE FIX)
# =========================
def generate_signal(df):
    close = float(df["Close"].iloc[-1])
    open_ = float(df["Open"].iloc[-1])

    if close > open_:
        return "BUY"
    else:
        return "SELL"

# =========================
# BIG MOVERS
# =========================
def big_movers(df, threshold=0.25):
    df = df.copy()
    df["pct"] = df["Close"].pct_change() * 100

    return df[abs(df["pct"]) > threshold]

# =========================
# UI
# =========================
st.title("🔥 NSE AI Smart Trader (CLEAN VERSION)")

symbol = st.text_input("Enter Symbol", "^NSEI")

df = load_data(symbol)

st.subheader("📊 Market Data")
st.dataframe(df.tail(20))

# =========================
# SMART MONEY
# =========================
bull, bear, trend = smart_money_engine(df)

st.subheader("🧠 Smart Money Flow")
st.write("Bullish Volume:", bull)
st.write("Bearish Volume:", bear)
st.success(f"Trend: {trend}")

# =========================
# SIGNAL
# =========================
signal = generate_signal(df)

st.subheader("⚡ Trading Signal")

if signal == "BUY":
    st.success("📈 BUY SIGNAL")
else:
    st.error("📉 SELL SIGNAL")

# =========================
# BIG MOVERS
# =========================
st.subheader("⚡ Big Movers")

moves = big_movers(df)

if not moves.empty:
    st.dataframe(moves.tail(20))
else:
    st.warning("No big moves detected")

# =========================
# SUMMARY PANEL
# =========================
st.subheader("📌 Summary")

st.info(f"""
Symbol: {symbol}
Trend: {trend}
Signal: {signal}
""")
