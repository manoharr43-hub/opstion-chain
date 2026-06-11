import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import pytz

# -------------------------------
# Streamlit Page Setup
# -------------------------------
st.set_page_config(
    page_title="HYBRID NSE PRO SCANNER V5",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .css-1r6slp0 { padding: 2rem; }
    .stSidebar { background-color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 HYBRID NSE PRO SCANNER V5")
st.write("EMA + RSI + Volume + Breakout Scanner + Correct IST Signal Time")

# -------------------------------
# Sidebar Configuration
# -------------------------------
with st.sidebar:
    st.header("⚙️ Configuration")
    st.info("Scanner V5 is optimized for Nifty 500 assets.")
    st.write("---")
    st.write("• **EMA:** 20/50 Cross")
    st.write("• **RSI:** 14-period")
    st.write("• **Volume:** 20-period SMA")

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
    period = st.selectbox("Period", ["5d","1mo","3mo","6mo"], index=0)

with col3:
    sector = st.selectbox("Sector", list(sector_stocks.keys()) + ["All NSE500"])

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
# Scanner Logic (Safe IST Time)
# -------------------------------
def scan_stock(df):
    if len(df) < 60:
        return None

    score = 0
    close = float(df["Close"].iloc[-1])

    # Safe timezone conversion
    ist = pytz.timezone("Asia/Kolkata")
    last_index = df.index[-1]
    if last_index.tzinfo is None:
        last_index = last_index.tz_localize("UTC")
    signal_time = last_index.astimezone(ist).strftime("%d-%b %Y %I:%M %p")

    ema_signal = "NEUTRAL"
    breakout_signal = "NO"
    volume_signal = "NO"

    # EMA Signal
    if df["EMA20"].iloc[-1] > df["EMA50"].iloc[-1]:
        score += 1
        ema_signal = "BUY"
    else:
        score -= 1
        ema_signal = "SELL"

    # RSI Signal
    rsi = float(df["RSI"].iloc[-1])
    if rsi > 60:
        score += 1
    elif rsi < 40:
        score -= 1

    # Breakout Signal
    breakout_high = df["High"].rolling(20).max().shift(1).iloc[-1]
    breakout_low = df["Low"].rolling(20).min().shift(1).iloc[-1]
    if close > breakout_high:
        score += 1
        breakout_signal = "BULLISH"
    elif close < breakout_low:
        score -= 1
        breakout_signal = "BEARISH"

    # Volume Spike
    avg_vol = float(df["AVG_VOL"].iloc[-1])
    current_vol = float(df["Volume"].iloc[-1])
    if avg_vol > 0 and current_vol > avg_vol * 1.5:
        score += 1
        volume_signal = "SPIKE"

    # Final Signal
    if score >= 3:
        final_signal = "STRONG BUY"
    elif score == 2:
        final_signal = "BUY"
    elif score <= -2:
        final_signal = "SELL"
    else:
        final_signal = "WAIT"

    return {
        "Price": round(close, 2),
        "EMA": ema_signal,
        "RSI": round(rsi, 2),
        "Breakout": breakout_signal,
        "Volume": volume_signal,
        "Score": score,
        "Signal": final_signal,
        "Time": signal_time
    }

# -------------------------------
# Run Scanner
# -------------------------------
if st.button("🚀 RUN SCAN"):
    results = []
    if sector == "All NSE500":
        selected_stocks = stocks[:100]  # limit for performance
    else:
        selected_stocks = sector_stocks[sector]

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
                signal["EMA"],
                signal["RSI"],
                signal["Breakout"],
                signal["Volume"],
                signal["Score"],
                signal["Signal"],
                signal["Time"]
            ])
        progress.progress((i + 1) / len(selected_stocks))

    result_df = pd.DataFrame(
        results,
        columns=["Stock","Price","EMA","RSI","Breakout","Volume","Score","Signal","Time"]
    )

    if not result_df.empty:
        result_df = result_df.sort_values(by="Score", ascending=False)
        st.success(f"Scan Completed : {len(result_df)} Stocks")
        st.dataframe(result_df, use_container_width=True)

        csv = result_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name="HybridScannerV5.csv",
            mime="text/csv"
        )
    else:
        st.warning("No signals found.")  back test add
