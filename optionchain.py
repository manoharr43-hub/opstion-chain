# NSE PRO SCANNER – NSE 500 Stocks Version
# Author: Manohar Custom Build

import yfinance as yf
import pandas as pd
import streamlit as st
import os

# -------------------------------
# CONFIG
# -------------------------------
@st.cache_data(ttl=86400)
def load_nse500():
    try:
        url = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
        df = pd.read_csv(url)
        return df['Symbol'].tolist()
    except:
        return ["RELIANCE","TCS","INFY","HDFCBANK","ICICIBANK"]  # fallback list

stocks = load_nse500()
interval = "15m"
period = "5d"

# -------------------------------
# FUNCTIONS
# -------------------------------
def load_data(stock):
    return yf.download(f"{stock}.NS", period=period, interval=interval)

def indicators(df):
    df["EMA20"] = df["Close"].ewm(span=20).mean()
    df["EMA50"] = df["Close"].ewm(span=50).mean()
    return df

def signal_logic(df):
    if df["EMA20"].iloc[-1] > df["EMA50"].iloc[-1]:
        return "BUY"
    elif df["EMA20"].iloc[-1] < df["EMA50"].iloc[-1]:
        return "SELL"
    else:
        return "WAIT"

def save_csv(df, stock):
    folder = "NSE500Reports"
    os.makedirs(folder, exist_ok=True)
    df.to_csv(f"{folder}/{stock}_report.csv")

# -------------------------------
# STREAMLIT UI
# -------------------------------
st.title("📊 NSE PRO SCANNER – NSE 500 Stocks")

tab1, tab2 = st.tabs(["🔴 LIVE SCAN", "📂 BACKTEST"])

with tab1:
    st.subheader("📡 LIVE SIGNALS")
    live_signals = []
    for stock in stocks[:50]:  # limit to first 50 for speed
        df = load_data(stock)
        df = indicators(df)
        sig = signal_logic(df)
        live_signals.append([stock, df["Close"].iloc[-1], sig])
    st.dataframe(pd.DataFrame(live_signals, columns=["Stock", "Price", "Signal"]))

with tab2:
    st.subheader("📂 BACKTEST REPORTS")
    for stock in stocks[:50]:
        df = load_data(stock)
        df = indicators(df)
        save_csv(df, stock)
    st.success("✅ Backtest CSV files saved in NSE500Reports folder")
