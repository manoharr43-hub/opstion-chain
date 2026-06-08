```python
# =========================================================
# 🚀 NSE PRO SCANNER V3.0
# =========================================================

import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import io
from datetime import datetime

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="NSE PRO SCANNER",
    layout="wide"
)

st.title("📊 NSE PRO SCANNER V3.0")

# =========================================================
# NSE STOCKS
# =========================================================

sector_stocks = {
    "Banking": ["HDFCBANK","ICICIBANK","SBIN","AXISBANK","KOTAKBANK"],
    "IT": ["TCS","INFY","WIPRO","HCLTECH","TECHM"],
    "Pharma": ["SUNPHARMA","CIPLA","DIVISLAB","DRREDDY","AUROPHARMA"],
    "Energy": ["RELIANCE","ONGC","BPCL","NTPC","POWERGRID"],
    "Auto": ["TATAMOTORS","M&M","EICHERMOT","HEROMOTOCO","BAJAJ-AUTO"],
    "FMCG": ["ITC","HINDUNILVR","BRITANNIA","DABUR","NESTLEIND"]
}

# =========================================================
# SETTINGS
# =========================================================

sector = st.sidebar.selectbox(
    "Select Sector",
    list(sector_stocks.keys())
)

stocks = sector_stocks[sector]

# =========================================================
# DATA
# =========================================================

@st.cache_data(ttl=300)
def load_data(symbol):

    try:
        df = yf.download(
            f"{symbol}.NS",
            period="3mo",
            interval="15m",
            progress=False,
            auto_adjust=True
        )

        return df

    except:
        return pd.DataFrame()

# =========================================================
# INDICATORS
# =========================================================

def add_indicators(df):

    if len(df) < 50:
        return df

    df["EMA20"] = df["Close"].ewm(span=20).mean()
    df["EMA50"] = df["Close"].ewm(span=50).mean()

    delta = df["Close"].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss

    df["RSI"] = 100 - (100/(1+rs))

    df["VOLAVG"] = df["Volume"].rolling(20).mean()

    return df

# =========================================================
# SIGNAL
# =========================================================

def get_signal(df):

    try:

        last = df.iloc[-1]

        buy = (
            last["EMA20"] > last["EMA50"]
            and last["RSI"] > 60
            and last["Volume"] > last["VOLAVG"]
        )

        sell = (
            last["EMA20"] < last["EMA50"]
            and last["RSI"] < 40
        )

        if buy:
            return "🟢 STRONG BUY"

        elif sell:
            return "🔴 SELL"

        else:
            return "🟡 WAIT"

    except:
        return "NO DATA"

# =========================================================
# SCAN
# =========================================================

if st.button("🚀 RUN SCANNER"):

    results = []

    progress = st.progress(0)

    for i, stock in enumerate(stocks):

        df = load_data(stock)

        if not df.empty:

            df = add_indicators(df)

            signal = get_signal(df)

            price = round(float(df["Close"].iloc[-1]), 2)

            rsi = round(float(df["RSI"].iloc[-1]), 2)

            volume = int(df["Volume"].iloc[-1])

            results.append([
                stock,
                price,
                rsi,
                volume,
                signal,
                datetime.now().strftime("%H:%M:%S")
            ])

        progress.progress((i+1)/len(stocks))

    report = pd.DataFrame(
        results,
        columns=[
            "Stock",
            "Price",
            "RSI",
            "Volume",
            "Signal",
            "Time"
        ]
    )

    st.success("Scan Complete")

    st.dataframe(
        report,
        use_container_width=True
    )

    # BUY SIGNALS

    buy_df = report[
        report["Signal"]=="🟢 STRONG BUY"
    ]

    st.subheader("🔥 Top Buy Signals")

    st.dataframe(
        buy_df,
        use_container_width=True
    )

    # Excel Download

    output = io.BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        report.to_excel(
            writer,
            sheet_name="Scanner",
            index=False
        )

    st.download_button(
        "📥 Download Excel",
        data=output.getvalue(),
        file_name="NSE_PRO_SCANNER.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
```
