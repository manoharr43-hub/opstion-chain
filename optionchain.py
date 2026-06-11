import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import pytz

# -------------------------------
# Streamlit Page Setup
# -------------------------------
st.set_page_config(page_title="HYBRID NSE PRO SCANNER V6", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .css-1r6slp0 { padding: 2rem; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 HYBRID NSE PRO SCANNER V6")
st.write("Support + Breakout + Breakdown + Big Volume Detection")

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
# User Inputs
# -------------------------------
col1, col2, col3 = st.columns(3)
with col1:
    interval = st.selectbox("Interval", ["5m","15m","30m","1h","1d"], index=1)
with col2:
    period = st.selectbox("Period", ["5d","1mo","3mo","6mo"], index=0)
with col3:
    stock_limit = st.slider("Number of Stocks", 50, 500, 500)

# -------------------------------
# Data Fetch
# -------------------------------
@st.cache_data(ttl=300)
def get_data(symbol, interval, period):
    try:
        df = yf.download(f"{symbol}.NS", interval=interval, period=period,
                         auto_adjust=True, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except:
        return pd.DataFrame()

# -------------------------------
# Indicators
# -------------------------------
def add_indicators(df):
    if len(df) < 60:
        return df
    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
    df["AVG_VOL"] = df["Volume"].rolling(20).mean()
    return df

# -------------------------------
# Scanner Logic
# -------------------------------
def scan_stock(df):
    if len(df) < 60:
        return None

    close = float(df["Close"].iloc[-1])
    ist = pytz.timezone("Asia/Kolkata")
    last_index = df.index[-1]
    if last_index.tzinfo is None:
        last_index = last_index.tz_localize("UTC")
    signal_time = last_index.astimezone(ist).strftime("%d-%b %Y %I:%M %p")

    # Support & Resistance (20-period)
    support = df["Low"].rolling(20).min().iloc[-1]
    resistance = df["High"].rolling(20).max().iloc[-1]

    breakout = "NO"
    breakdown = "NO"
    if close > resistance:
        breakout = "BULLISH BREAKOUT"
    elif close < support:
        breakdown = "BEARISH BREAKDOWN"

    # Big Volume
    avg_vol = float(df["AVG_VOL"].iloc[-1])
    current_vol = float(df["Volume"].iloc[-1])
    big_volume = "NO"
    if avg_vol > 0 and current_vol > avg_vol * 2:
        big_volume = "🔥 BIG VOLUME"

    return {
        "Price": round(close, 2),
        "Support": round(support, 2),
        "Resistance": round(resistance, 2),
        "Breakout": breakout,
        "Breakdown": breakdown,
        "Volume": big_volume,
        "Time": signal_time
    }

# -------------------------------
# Run Scanner
# -------------------------------
if st.button("🚀 RUN SCAN"):
    results = []
    selected_stocks = stocks[:stock_limit]
    progress = st.progress(0)

    for i, symbol in enumerate(selected_stocks):
        df = get_data(symbol, interval, period)
        if df.empty:
            continue
        df = add_indicators(df)
        signal = scan_stock(df)
        if signal:
            results.append([
                symbol,
                signal["Price"],
                signal["Support"],
                signal["Resistance"],
                signal["Breakout"],
                signal["Breakdown"],
                signal["Volume"],
                signal["Time"]
            ])
        progress.progress((i + 1) / len(selected_stocks))

    result_df = pd.DataFrame(
        results,
        columns=["Stock","Price","Support","Resistance","Breakout","Breakdown","Volume","Time"]
    )

    if not result_df.empty:
        st.success(f"Scan Completed : {len(result_df)} Stocks")
        st.dataframe(result_df, use_container_width=True)
        csv = result_df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download CSV", csv, "HybridScannerV6.csv", "text/csv")
    else:
        st.warning("No signals found.")
