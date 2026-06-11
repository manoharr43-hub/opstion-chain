# HYBRID NSE PRO SCANNER – EMA + Breakout Channels
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
        return ["RELIANCE","TCS","INFY","HDFCBANK","ICICIBANK"]

stocks = load_nse500()
interval = "15m"
period = "5d"

sector_stocks = {
    "Banking": ["HDFCBANK","ICICIBANK","SBIN","AXISBANK","KOTAKBANK"],
    "IT": ["TCS","INFY","WIPRO","HCLTECH","TECHM"],
    "Pharma": ["SUNPHARMA","CIPLA","DIVISLAB","DRREDDY","AUROPHARMA"],
    "Energy": ["RELIANCE","ONGC","BPCL","NTPC","POWERGRID"],
    "Auto": ["TATAMOTORS","M&M","EICHERMOT","HEROMOTOCO","BAJAJ-AUTO"],
    "FMCG": ["HINDUNILVR","ITC","NESTLEIND","BRITANNIA","DABUR"]
}

# -------------------------------
# FUNCTIONS
# -------------------------------
def load_data(stock):
    try:
        df = yf.download(f"{stock}.NS", period=period, interval=interval)
        return df
    except Exception as e:
        st.error(f"Error loading {stock}: {e}")
        return pd.DataFrame()

def indicators(df):
    if df.empty:
        return df
    df["EMA20"] = df["Close"].ewm(span=20).mean()
    df["EMA50"] = df["Close"].ewm(span=50).mean()
    return df

def ema_signal(df):
    if df.empty or len(df) == 0:
        return "NO DATA"
    if df["EMA20"].iloc[-1] > df["EMA50"].iloc[-1]:
        return "BUY"
    elif df["EMA20"].iloc[-1] < df["EMA50"].iloc[-1]:
        return "SELL"
    else:
        return "WAIT"

def breakout_signal(df):
    if df.empty or len(df) < 20:
        return "NO DATA"
    high = df["High"].rolling(20).max().iloc[-1]
    low = df["Low"].rolling(20).min().iloc[-1]
    close = df["Close"].iloc[-1]   # ✅ single float value
    if close > high:
        return "Bullish Breakout ▲"
    elif close < low:
        return "Bearish Breakout ▼"
    else:
        return "Inside Channel"

def save_csv(df, stock):
    if df.empty:
        return
    folder = "HybridReports"
    os.makedirs(folder, exist_ok=True)
    df.to_csv(f"{folder}/{stock}_report.csv")

# -------------------------------
# STREAMLIT UI
# -------------------------------
st.title("📊 HYBRID NSE PRO SCANNER – Final Clean E Code")

sector = st.selectbox("Select Sector", list(sector_stocks.keys()) + ["All NSE 500"])

tab1, tab2 = st.tabs(["🔴 LIVE SCAN", "📂 BACKTEST"])

with tab1:
    st.subheader("📡 LIVE SIGNALS")
    live_signals = []
    selected_stocks = sector_stocks[sector] if sector != "All NSE 500" else stocks[:50]
    for stock in selected_stocks:
        df = load_data(stock)
        df = indicators(df)
        sig_ema = ema_signal(df)
        sig_breakout = breakout_signal(df)
        price = df["Close"].iloc[-1] if not df.empty else "NA"
        live_signals.append([stock, price, sig_ema, sig_breakout])
    st.dataframe(pd.DataFrame(live_signals, columns=["Stock","Price","EMA Signal","Breakout Signal"]))

with tab2:
    st.subheader("📂 BACKTEST REPORTS")
    for stock in selected_stocks:
        df = load_data(stock)
        df = indicators(df)
        save_csv(df, stock)
    st.success("✅ Backtest CSV files saved in HybridReports folder")
    st.download_button(
        label="📂 Download Backtest Excel",
        data=pd.DataFrame(live_signals).to_csv(index=False),
        file_name="Hybrid_Backtest_Report.csv",
        mime="text/csv"
    )
