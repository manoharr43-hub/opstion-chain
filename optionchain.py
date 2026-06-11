import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import pytz

# -------------------------------
# Streamlit Page Setup
# -------------------------------
st.set_page_config(
    page_title="HYBRID NSE PRO SCANNER V6",
    layout="wide"
)

st.title("📊 HYBRID NSE PRO SCANNER V6")
st.write("EMA + RSI + Volume + Breakout Scanner + Backtest Module + Correct IST Signal Time")

# -------------------------------
# Load NSE500 Stocks
# -------------------------------
@st.cache_data(ttl=86400)
def load_nse500():
    try:
        url = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
        df = pd.read_csv(url)
        return sorted(df["Symbol"].dropna().unique().tolist())
    except:
        return ["RELIANCE","TCS","INFY","HDFCBANK","ICICIBANK","SBIN","ITC","LT"]

stocks = load_nse500()

# -------------------------------
# Data Fetch
# -------------------------------
@st.cache_data(ttl=300)
def get_data(symbol, interval, period):
    try:
        df = yf.download(
            f"{symbol}.NS",
            interval=interval,
            period=period,
            auto_adjust=True,
            progress=False
        )
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except:
        return pd.DataFrame()

# -------------------------------
# RSI Calculation
# -------------------------------
def calculate_rsi(df, period=14):
    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# -------------------------------
# Add Indicators
# -------------------------------
def add_indicators(df):
    if len(df) < 60:
        return df
    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
    df["RSI"] = calculate_rsi(df)
    df["AVG_VOL"] = df["Volume"].rolling(20).mean()
    return df

# -------------------------------
# Breakout Backtest Logic
# -------------------------------
def backtest_breakouts(df):
    results = []
    ist = pytz.timezone("Asia/Kolkata")

    for i in range(20, len(df)):
        close = df["Close"].iloc[i]
        high = df["High"].rolling(20).max().shift(1).iloc[i]
        low = df["Low"].rolling(20).min().shift(1).iloc[i]
        vol = df["Volume"].iloc[i]
        avg_vol = df["AVG_VOL"].iloc[i]

        breakout_type = None
        result = "WAIT"

        if close > high:
            breakout_type = "Bullish"
            if vol > avg_vol * 1.5:
                result = "Success"
            else:
                result = "Failure"

        elif close < low:
            breakout_type = "Bearish"
            if vol > avg_vol * 1.5:
                result = "Success"
            else:
                result = "Failure"

        if breakout_type:
            time = df.index[i]
            if time.tzinfo is None:
                time = time.tz_localize("UTC")
            signal_time = time.astimezone(ist).strftime("%d-%b %Y %I:%M %p")

            results.append([signal_time, breakout_type, round(close,2), vol, avg_vol, result])

    return pd.DataFrame(results, columns=["Time","Breakout","Price","Volume","AvgVol","Result"])

# -------------------------------
# Run Backtest
# -------------------------------
symbol = st.selectbox("Select Stock", stocks)
interval = st.selectbox("Interval", ["15m","30m","1h","1d"], index=1)
period = st.selectbox("Period", ["1mo","3mo","6mo"], index=0)

if st.button("🔎 Run Backtest"):
    df = get_data(symbol, interval, period)
    if not df.empty:
        df = add_indicators(df)
        bt = backtest_breakouts(df)
        if not bt.empty:
            st.success(f"Backtest Completed: {len(bt)} Breakout Events")
            st.dataframe(bt, use_container_width=True)

            csv = bt.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Backtest CSV",
                data=csv,
                file_name=f"{symbol}_BreakoutBacktest.csv",
                mime="text/csv"
            )
        else:
            st.warning("No breakout events found.")
    else:
        st.error("Data not available for this stock.")
