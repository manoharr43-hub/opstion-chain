import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import io
from datetime import datetime

st.set_page_config(
page_title="NSE AI PRO MAX",
layout="wide"
)

st.title("🚀 NSE AI PRO MAX")

NSE_STOCKS = [
"RELIANCE",
"TCS",
"INFY",
"HDFCBANK",
"ICICIBANK",
"SBIN",
"AXISBANK",
"KOTAKBANK",
"ITC",
"LT"
]

@st.cache_data(ttl=300)
def load_stock(symbol):
try:
df = yf.download(
f"{symbol}.NS",
period="3mo",
interval="1d",
progress=False,
auto_adjust=True
)

```
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    return df

except Exception:
    return pd.DataFrame()
```

def calculate_indicators(df):

```
if len(df) < 50:
    return df

close = df["Close"]

df["EMA20"] = close.ewm(span=20).mean()
df["EMA50"] = close.ewm(span=50).mean()

delta = close.diff()

gain = delta.where(delta > 0, 0)
loss = -delta.where(delta < 0, 0)

avg_gain = gain.rolling(14).mean()
avg_loss = loss.rolling(14).mean()

rs = avg_gain / avg_loss

df["RSI"] = 100 - (100 / (1 + rs))

df["VOL_AVG"] = df["Volume"].rolling(20).mean()

return df
```

def generate_signal(df):

```
try:

    last = df.iloc[-1]

    if (
        last["EMA20"] > last["EMA50"]
        and last["RSI"] > 60
        and last["Volume"] > last["VOL_AVG"]
    ):
        return "BUY"

    if (
        last["EMA20"] < last["EMA50"]
        and last["RSI"] < 40
    ):
        return "SELL"

    return "WAIT"

except Exception:
    return "NO DATA"
```

if st.button("SCAN MARKET"):

```
results = []

progress = st.progress(0)

for i, stock in enumerate(NSE_STOCKS):

    df = load_stock(stock)

    if not df.empty:

        df = calculate_indicators(df)

        signal = generate_signal(df)

        price = round(float(df["Close"].iloc[-1]), 2)

        rsi = round(float(df["RSI"].iloc[-1]), 2)

        results.append([
            stock,
            price,
            rsi,
            signal,
            datetime.now().strftime("%H:%M:%S")
        ])

    progress.progress((i + 1) / len(NSE_STOCKS))

report = pd.DataFrame(
    results,
    columns=[
        "Stock",
        "Price",
        "RSI",
        "Signal",
        "Time"
    ]
)

st.dataframe(report, use_container_width=True)

buy_df = report[report["Signal"] == "BUY"]

st.subheader("Top BUY Signals")

st.dataframe(buy_df, use_container_width=True)

output = io.BytesIO()

with pd.ExcelWriter(
    output,
    engine="openpyxl"
) as writer:

    report.to_excel(
        writer,
        index=False,
        sheet_name="Scanner"
    )

st.download_button(
    "Download Excel",
    output.getvalue(),
    file_name="NSE_AI_PRO_MAX.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
```
