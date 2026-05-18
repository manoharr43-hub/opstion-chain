# ==========================================
# optionchain.py — NSE Option Chain Dashboard
# ==========================================
import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np

st.set_page_config(page_title="NSE Option Chain AI PRO", layout="wide")

# =============================
# Load NSE Top 500 Stocks
# =============================
@st.cache_data(ttl=86400)
def load_nse500():
    try:
        url = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
        df = pd.read_csv(url)
        return df['Symbol'].tolist()
    except Exception:
        return ["RELIANCE", "HDFCBANK", "INFY"]

stocks = load_nse500()

# =============================
# Sidebar Settings
# =============================
st.sidebar.header("Scanner Settings")
selected_stock = st.sidebar.selectbox("Choose Stock", stocks)
interval = st.sidebar.selectbox("Interval", ["5m", "15m", "30m", "1h", "1d"])
period = st.sidebar.selectbox("Period", ["5d", "1mo", "3mo"])

# =============================
# Fetch Data
# =============================
@st.cache_data(ttl=3600)
def get_data(symbol, period, interval):
    data = yf.download(symbol + ".NS", period=period, interval=interval)
    return data

df = get_data(selected_stock, period, interval)

if df.empty:
    st.error("⚠️ No data available for selected stock or interval.")
    st.stop()

# =============================
# Indicators
# =============================
df['EMA20'] = df['Close'].ewm(span=20).mean()
df['EMA50'] = df['Close'].ewm(span=50).mean()

# Safe RSI Calculation
delta = df['Close'].diff()
gain = delta.clip(lower=0)
loss = -delta.clip(upper=0)
avg_gain = gain.rolling(14).mean()
avg_loss = loss.rolling(14).mean()
rs = avg_gain / avg_loss
df['RSI'] = 100 - (100 / (1 + rs))
df['RSI'].fillna(50, inplace=True)

# Safe VWAP Calculation (Series)
df['VWAP'] = ((df['Close'] * df['Volume']).cumsum() / df['Volume'].cumsum()).astype(float)

# ATR Calculation
df['TR'] = np.maximum(df['High'] - df['Low'],
                      np.maximum(abs(df['High'] - df['Close'].shift()),
                                 abs(df['Low'] - df['Close'].shift())))
df['ATR'] = df['TR'].rolling(14).mean()

df.dropna(inplace=True)

# =============================
# Signal Logic
# =============================
df['BUY'] = (
    (df['EMA20'] > df['EMA50']) &
    (df['Close'] > df['VWAP']) &
    (df['RSI'] > 55)
)

df['SELL'] = (
    (df['EMA20'] < df['EMA50']) &
    (df['Close'] < df['VWAP']) &
    (df['RSI'] < 45)
)

# =============================
# Dashboard
# =============================
st.title("📊 NSE Option Chain AI PRO")
st.subheader(f"Stock: {selected_stock}")

latest = df.iloc[-1]
trend = "BULLISH" if latest['EMA20'] > latest['EMA50'] else "BEARISH"
signal = "🚀 BUY" if latest['BUY'] else "🔻 SELL" if latest['SELL'] else "WAIT"

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Trend", trend)
col2.metric("RSI", f"{latest['RSI']:.2f}")
col3.metric("VWAP", "ABOVE" if latest['Close'] > latest['VWAP'] else "BELOW")
col4.metric("Signal", signal)
col5.metric("ATR", f"{latest['ATR']:.2f}")
col6.metric("Volume", f"{latest['Volume']:.0f}")

st.line_chart(df[['Close', 'EMA20', 'EMA50', 'VWAP']])
st.dataframe(df.tail(10))
