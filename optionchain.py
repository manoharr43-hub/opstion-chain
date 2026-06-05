# NSE PRO SCANNER – Sector Wise Version
# Author: Manohar Custom Build

import yfinance as yf
import pandas as pd
import streamlit as st

# -------------------------------
# CONFIG
# -------------------------------
sector_stocks = {
    "Banking": ["HDFCBANK","ICICIBANK","SBIN","AXISBANK","KOTAKBANK"],
    "IT": ["TCS","INFY","WIPRO","HCLTECH","TECHM"],
    "Pharma": ["SUNPHARMA","CIPLA","DIVISLAB","DRREDDY","AUROPHARMA"],
    "Energy": ["RELIANCE","ONGC","BPCL","NTPC","POWERGRID"],
    "Auto": ["TATAMOTORS","M&M","EICHERMOT","HEROMOTOCO","BAJAJ-AUTO"],
    "FMCG": ["HINDUNILVR","ITC","NESTLEIND","BRITANNIA","DABUR"]
}

interval = "15m"
period = "5d"

# -------------------------------
# FUNCTIONS
# -------------------------------
def load_data(stock):
    try:
        df = yf.download(f"{stock}.NS", period=period, interval=interval)
        return df
    except:
        return pd.DataFrame()

def indicators(df):
    if df.empty:
        return df
    df["EMA20"] = df["Close"].ewm(span=20).mean()
    df["EMA50"] = df["Close"].ewm(span=50).mean()
    return df

def signal_logic(df):
    if df.empty or len(df) == 0:
        return "NO DATA"
    if df["EMA20"].iloc[-1] > df["EMA50"].iloc[-1]:
        return "BUY"
    elif df["EMA20"].iloc[-1] < df["EMA50"].iloc[-1]:
        return "SELL"
    else:
        return "WAIT"

# -------------------------------
# STREAMLIT UI
# -------------------------------
st.title("📊 NSE PRO SCANNER – Sector Wise")

sector = st.selectbox("Select Sector", list(sector_stocks.keys()))

signals = []
for stock in sector_stocks[sector]:
    df = load_data(stock)
    df = indicators(df)
    sig = signal_logic(df)
    price = df["Close"].iloc[-1] if not df.empty else "NA"
    signals.append([stock, price, sig])

st.dataframe(pd.DataFrame(signals, columns=["Stock","Price","Signal"]))
