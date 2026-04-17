import streamlit as st
import requests
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
import time

# =============================
# CONFIG
# =============================
st.set_page_config(page_title="🔥 NSE PRO", layout="wide")
st_autorefresh(interval=20000, key="refresh")

st.title("🚀 NSE OPTION CHAIN + INTRADAY PRO")

# =============================
# NSE OPTION CHAIN (RETRY FIX)
# =============================
@st.cache_data(ttl=20)
def get_option_chain(symbol):

    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Referer": "https://www.nseindia.com/",
    }

    session = requests.Session()

    for i in range(3):  # retry 3 times
        try:
            session.get("https://www.nseindia.com", headers=headers, timeout=5)
            res = session.get(url, headers=headers, timeout=5)

            if res.status_code == 200:
                data = res.json()
                return data.get("records", {}).get("data", [])

        except:
            time.sleep(1)

    return []

# =============================
# USER INPUT
# =============================
symbol = st.sidebar.selectbox("Select Index", ["NIFTY", "BANKNIFTY"])

# =============================
# OPTION CHAIN
# =============================
data = get_option_chain(symbol)

calls, puts = [], []

for row in data:
    ce = row.get("CE")
    pe = row.get("PE")

    if ce:
        calls.append([ce["strikePrice"], ce["openInterest"], ce["lastPrice"]])

    if pe:
        puts.append([pe["strikePrice"], pe["openInterest"], pe["lastPrice"]])

call_df = pd.DataFrame(calls, columns=["Strike", "OI", "LTP"])
put_df = pd.DataFrame(puts, columns=["Strike", "OI", "LTP"])

col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 CALLS")
    st.dataframe(call_df, use_container_width=True)

with col2:
    st.subheader("📉 PUTS")
    st.dataframe(put_df, use_container_width=True)

# =============================
# PCR
# =============================
if not call_df.empty and not put_df.empty:
    pcr = round(put_df["OI"].sum() / call_df["OI"].sum(), 2)
else:
    pcr = 0

st.metric("PCR", pcr)

# =============================
# SPOT PRICE (STRIKE LEVEL)
# =============================
ticker_symbol = "^NSEI" if symbol == "NIFTY" else "^NSEBANK"

spot = yf.download(ticker_symbol, period="1d", interval="1m", progress=False)

if not spot.empty:
    current_price = float(spot["Close"].iloc[-1])
    st.success(f"📍 Current Spot Price: {round(current_price,2)}")

# =============================
# INTRADAY SIGNALS
# =============================
st.subheader("⏱️ Intraday Signals (9:15 - 3:30)")

df = yf.download(ticker_symbol, period="1d", interval="5m", progress=False)

if df.empty:
    st.warning("No data (Market Closed)")
else:
    df = df.between_time("09:15", "15:30")

    # FIX FLOAT ISSUE
    df["Close"] = df["Close"].astype(float)

    # EMA
    df["EMA9"] = df["Close"].ewm(span=9).mean()
    df["EMA21"] = df["Close"].ewm(span=21).mean()

    signals = []

    for i in range(1, len(df)):
        signal = "HOLD"

        if df["EMA9"].iloc[i] > df["EMA21"].iloc[i] and df["EMA9"].iloc[i-1] <= df["EMA21"].iloc[i-1]:
            signal = "BUY 🚀"

        elif df["EMA9"].iloc[i] < df["EMA21"].iloc[i] and df["EMA9"].iloc[i-1] >= df["EMA21"].iloc[i-1]:
            signal = "SELL 🔻"

        signals.append({
            "Time": df.index[i].strftime("%H:%M"),
            "Price": round(float(df["Close"].iloc[i]),2),
            "EMA9": round(df["EMA9"].iloc[i],2),
            "EMA21": round(df["EMA21"].iloc[i],2),
            "Signal": signal
        })

    signal_df = pd.DataFrame(signals)

    st.dataframe(signal_df, use_container_width=True)

    # LAST SIGNAL
    if not signal_df.empty:
        st.info(f"📢 Latest Signal: {signal_df.iloc[-1]['Signal']}")
