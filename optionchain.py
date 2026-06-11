```python
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import io

# =====================================================
# HYBRID NSE PRO SCANNER V2
# =====================================================

st.set_page_config(
    page_title="HYBRID NSE PRO SCANNER V2",
    layout="wide"
)

st.title("📊 HYBRID NSE PRO SCANNER V2")
st.caption("EMA + RSI + Volume + Breakout Scanner")

# =====================================================
# NSE STOCKS
# =====================================================

@st.cache_data(ttl=86400)
def load_nse500():
    try:
        url = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
        df = pd.read_csv(url)
        return sorted(df["Symbol"].dropna().unique().tolist())
    except:
        return [
            "RELIANCE","TCS","INFY","HDFCBANK","ICICIBANK",
            "SBIN","AXISBANK","KOTAKBANK","ITC","LT"
        ]

stocks = load_nse500()

sector_stocks = {
    "Banking":["HDFCBANK","ICICIBANK","SBIN","AXISBANK","KOTAKBANK"],
    "IT":["TCS","INFY","WIPRO","HCLTECH","TECHM"],
    "Pharma":["SUNPHARMA","CIPLA","DIVISLAB","DRREDDY"],
    "Energy":["RELIANCE","ONGC","BPCL","NTPC"],
    "Auto":["TATAMOTORS","M&M","EICHERMOT","HEROMOTOCO"],
    "FMCG":["ITC","HINDUNILVR","BRITANNIA","DABUR"]
}

# =====================================================
# SETTINGS
# =====================================================

col1,col2,col3 = st.columns(3)

with col1:
    interval = st.selectbox(
        "Interval",
        ["5m","15m","30m","1h","1d"],
        index=1
    )

with col2:
    period = st.selectbox(
        "Period",
        ["5d","1mo","3mo","6mo"],
        index=0
    )

with col3:
    sector = st.selectbox(
        "Sector",
        list(sector_stocks.keys()) + ["All NSE500"]
    )

# =====================================================
# DATA
# =====================================================

@st.cache_data(ttl=300)
def get_data(symbol):
    try:
        df = yf.download(
            f"{symbol}.NS",
            interval=interval,
            period=period,
            auto_adjust=True,
            progress=False
        )
        return df
    except:
        return pd.DataFrame()

# =====================================================
# RSI
# =====================================================

def calculate_rsi(df, period=14):

    delta = df["Close"].diff()

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))

    return rsi

# =====================================================
# INDICATORS
# =====================================================

def add_indicators(df):

    if len(df) < 60:
        return df

    df["EMA20"] = df["Close"].ewm(span=20).mean()

    df["EMA50"] = df["Close"].ewm(span=50).mean()

    df["RSI"] = calculate_rsi(df)

    df["AVG_VOL"] = df["Volume"].rolling(20).mean()

    return df

# =====================================================
# SIGNAL ENGINE
# =====================================================

def scan_stock(df):

    if len(df) < 60:
        return None

    score = 0

    ema_signal = "NEUTRAL"
    breakout_signal = "NO"
    volume_signal = "NO"

    close = float(df["Close"].iloc[-1])

    # EMA

    if (
        df["EMA20"].iloc[-1] > df["EMA50"].iloc[-1]
    ):
        score += 1
        ema_signal = "BUY"

    else:
        score -= 1
        ema_signal = "SELL"

    # RSI

    rsi = float(df["RSI"].iloc[-1])

    if rsi > 60:
        score += 1

    if rsi < 40:
        score -= 1

    # Breakout

    breakout_high = (
        df["High"]
        .rolling(20)
        .max()
        .shift(1)
        .iloc[-1]
    )

    if close > breakout_high:
        score += 1
        breakout_signal = "BULLISH"

    # Volume

    avg_vol = float(df["AVG_VOL"].iloc[-1])

    current_vol = float(df["Volume"].iloc[-1])

    if current_vol > avg_vol * 1.5:
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
        "Price": round(close,2),
        "EMA": ema_signal,
        "RSI": round(rsi,2),
        "Breakout": breakout_signal,
        "Volume": volume_signal,
        "Score": score,
        "Signal": final_signal
    }

# =====================================================
# SCAN BUTTON
# =====================================================

if st.button("🚀 RUN SCAN"):

    results = []

    if sector == "All NSE500":
        selected = stocks[:100]
    else:
        selected = sector_stocks[sector]

    progress = st.progress(0)

    for i,symbol in enumerate(selected):

        df = get_data(symbol)

        if len(df) == 0:
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
                signal["Signal"]
            ])

        progress.progress((i+1)/len(selected))

    result_df = pd.DataFrame(
        results,
        columns=[
            "Stock",
            "Price",
            "EMA",
            "RSI",
            "Breakout",
            "Volume",
            "Score",
            "Signal"
        ]
    )

    result_df = result_df.sort_values(
        "Score",
        ascending=False
    )

    st.success(
        f"Scan Completed: {len(result_df)} Stocks"
    )

    st.dataframe(
        result_df,
        use_container_width=True
    )

    csv = result_df.to_csv(index=False)

    st.download_button(
        "📥 Download CSV",
        data=csv,
        file_name="HybridScannerV2.csv",
        mime="text/csv"
    )
```
