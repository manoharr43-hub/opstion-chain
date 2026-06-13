import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import pytz
import requests
import io
from concurrent.futures import ThreadPoolExecutor, as_completed

# -------------------------------
# Streamlit Page Setup
# -------------------------------
st.set_page_config(page_title="HYBRID NSE PRO SCANNER V6.4", layout="wide")

st.title("📊 HYBRID NSE PRO SCANNER V6.4")
st.write("EMA + RSI + Breakout + MACD + VWAP + Supertrend + 52W Range | Excel & Time")

# -------------------------------
# Sidebar Configuration
# -------------------------------
with st.sidebar:
    st.header("⚙️ Configuration")
    st.info("Scanner V6.4 includes interval-safe VWAP, optimized caching & Excel Export.")
    st.write("---")
    st.write("• **EMA:** 20/50 Cross")
    st.write("• **RSI:** 14-period")
    st.write("• **Breakout:** 20-period High/Low")
    st.write("• **MACD:** 12, 26, 9")
    st.write("• **Supertrend:** 10, 3")
    st.write("• **VWAP:** Intraday Anchored")

# -------------------------------
# Load NSE500 Stocks
# -------------------------------
@st.cache_data(ttl=86400)
def load_nse500():
    try:
        url = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        df = pd.read_csv(io.StringIO(response.text))
        return sorted(df["Symbol"].dropna().unique().tolist())
    except:
        return ["RELIANCE","TCS","INFY","HDFCBANK","ICICIBANK","SBIN","ITC","LT","AXISBANK","KOTAKBANK"]

stocks = load_nse500()

sector_stocks = {
    "Banking": ["HDFCBANK","ICICIBANK","SBIN","AXISBANK","KOTAKBANK"],
    "IT": ["TCS","INFY","WIPRO","HCLTECH","TECHM"],
    "Pharma": ["SUNPHARMA","CIPLA","DIVISLAB","DRREDDY"],
    "Energy": ["RELIANCE","ONGC","BPCL","NTPC"],
    "Auto": ["TATAMOTORS","M&M","EICHERMOT","HEROMOTOCO"],
    "FMCG": ["ITC","HINDUNILVR","BRITANNIA","DABUR"]
}

# -------------------------------
# User Inputs
# -------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    interval = st.selectbox("Interval", ["5m","15m","30m","1h","1d"], index=1)

with col2:
    period = st.selectbox("Period", ["5d","1mo","3mo","6mo", "1y"], index=1)

with col3:
    sector = st.selectbox("Sector", list(sector_stocks.keys()) + ["All NSE500"])

# -------------------------------
# Data Fetch
# -------------------------------
@st.cache_data(ttl=300)
def get_data(symbol, interval, period):
    try:
        df = yf.download(f"{symbol}.NS", interval=interval, period=period, auto_adjust=True, progress=False)
        if isinstance(df.columns, pd.MultiIndex): 
            df.columns = df.columns.get_level_values(0)
        return df
    except:
        return pd.DataFrame()

# -------------------------------
# Indicators Logic (Interval Safe)
# -------------------------------
def calculate_supertrend(df, period=10, multiplier=3):
    high, low, close = df['High'], df['Low'], df['Close']
    tr = np.maximum(high - low, np.maximum(abs(high - close.shift(1)), abs(low - close.shift(1))))
    atr = tr.rolling(window=period).mean()
    hl2 = (high + low) / 2
    upperband = hl2 + (multiplier * atr)
    lowerband = hl2 - (multiplier * atr)
    supertrend, direction = np.zeros(len(df)), np.zeros(len(df))
    for i in range(1, len(df)):
        if close.iloc[i] > upperband.iloc[i-1]: direction[i] = 1
        elif close.iloc[i] < lowerband.iloc[i-1]: direction[i] = -1
        else: direction[i] = direction[i-1]
        supertrend[i] = lowerband.iloc[i] if direction[i] == 1 else upperband.iloc[i]
    df['Supertrend'], df['ST_Direction'] = supertrend, direction
    return df

def add_indicators(df, interval):
    if len(df) < 60: return df
    df["EMA20"] = df["Close"].ewm(span=20).mean()
    df["EMA50"] = df["Close"].ewm(span=50).mean()
    delta = df["Close"].diff()
    df["RSI"] = 100 - (100 / (1 + (delta.clip(lower=0).ewm(com=13).mean() / -delta.clip(upper=0).ewm(com=13).mean())))
    df["MACD_Line"] = df["Close"].ewm(span=12).mean() - df["Close"].ewm(span=26).mean()
    df["Signal_Line"] = df["MACD_Line"].ewm(span=9).mean()
    df["MACD_Hist"] = df["MACD_Line"] - df["Signal_Line"]
    tp = (df['High'] + df['Low'] + df['Close']) / 3
    if 'd' not in interval and 'wk' not in interval and 'mo' not in interval:
        df['Date'] = df.index.date
        df['VWAP'] = (df['Volume'] * tp).groupby(df['Date']).cumsum() / df['Volume'].groupby(df['Date']).cumsum()
    else:
        df['VWAP'] = (df['Volume'] * tp).rolling(20).sum() / df['Volume'].rolling(20).sum()
    df = calculate_supertrend(df)
    df["AVG_VOL"] = df["Volume"].rolling(20).mean()
    return df

# -------------------------------
# Scanner Logic
# -------------------------------
def scan_stock(df):
    if len(df) < 60: return None
    score, close = 0, float(df["Close"].iloc[-1])
    ist = pytz.timezone("Asia/Kolkata")
    last_index = df.index[-1]
    if last_index.tzinfo is None: last_index = last_index.tz_localize("UTC")
    signal_time = last_index.astimezone(ist).strftime("%d-%b %Y %I:%M %p")
    if df["EMA20"].iloc[-1] > df["EMA50"].iloc[-1]: score += 1
    else: score -= 1
    rsi = float(df["RSI"].iloc[-1])
    if rsi > 60: score += 1
    elif rsi < 40: score -= 1
    breakout_high = df["High"].rolling(20).max().shift(1).iloc[-1]
    breakout_low = df["Low"].rolling(20).min().shift(1).iloc[-1]
    breakout_signal = "BULLISH" if close > breakout_high else "BEARISH" if close < breakout_low else "NO"
    if breakout_signal == "BULLISH": score += 1
    elif breakout_signal == "BEARISH": score -= 1
    macd = "BULLISH" if df["MACD_Line"].iloc[-1] > df["Signal_Line"].iloc[-1] else "BEARISH"
    score += 1 if macd == "BULLISH" else -1
    st_dir = "UP" if df["ST_Direction"].iloc[-1] == 1 else "DOWN"
    score += 1 if st_dir == "UP" else -1
    vwap_val = float(df["VWAP"].iloc[-1])
    vwap_sig = "ABOVE" if close > vwap_val else "BELOW"
    score += 1 if vwap_sig == "ABOVE" else -1
    if float(df["Volume"].iloc[-1]) > float(df["AVG_VOL"].iloc[-1]) * 1.5:
        score += 1 if close > df["Open"].iloc[-1] else -1
    if score >= 4: signal = "STRONG BUY"
    elif score >= 2: signal = "BUY"
    elif score <= -4: signal = "STRONG SELL"
    elif score <= -2: signal = "SELL"
    else: signal = "WAIT"
    return {
        "Price": round(close, 2),
        "RSI":
