import streamlit as st
import requests
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
import time

# =============================
# CONFIG
# =============================
st.set_page_config(page_title="🔥 NSE AI PRO MAX", layout="wide")
st_autorefresh(interval=20000, key="refresh")

st.title("🚀 NSE OPTION CHAIN + INTRADAY AI PRO MAX")

# =============================
# NSE OPTION CHAIN
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

    for _ in range(3):
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
# OPTION DATA
# =============================
data = get_option_chain(symbol)

calls, puts = [], []

for row in data:
    ce = row.get("CE")
    pe = row.get("PE")

    if ce:
        calls.append({
            "Strike": ce.get("strikePrice", 0),
            "OI": ce.get("openInterest", 0),
            "Chg OI": ce.get("changeinOpenInterest", 0),
            "LTP": ce.get("lastPrice", 0)
        })

    if pe:
        puts.append({
            "Strike": pe.get("strikePrice", 0),
            "OI": pe.get("openInterest", 0),
            "Chg OI": pe.get("changeinOpenInterest", 0),
            "LTP": pe.get("lastPrice", 0)
        })

call_df = pd.DataFrame(calls)
put_df = pd.DataFrame(puts)

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
pcr = 0
if not call_df.empty and not put_df.empty:
    try:
        pcr = round(put_df["OI"].sum() / call_df["OI"].sum(), 2)
    except:
        pcr = 0

st.metric("PCR", pcr)

# =============================
# SPOT PRICE (SAFE)
# =============================
ticker_symbol = "^NSEI" if symbol == "NIFTY" else "^NSEBANK"
current_price = None

try:
    spot = yf.download(ticker_symbol, period="1d", interval="5m", progress=False)

    if spot is not None and not spot.empty:

        if isinstance(spot.columns, pd.MultiIndex):
            spot.columns = spot.columns.get_level_values(0)

        if "Close" in spot.columns:
            close_series = pd.to_numeric(spot["Close"], errors="coerce").dropna()

            if not close_series.empty:
                current_price = float(close_series.iloc[-1])
                st.success(f"📍 Spot Price: {round(current_price,2)}")

except:
    st.warning("Spot error")

# =============================
# ATM STRIKE
# =============================
atm = None

if current_price:
    atm = round(current_price / 50) * 50
    st.info(f"🎯 ATM Strike: {atm}")

# =============================
# OI SUPPORT / RESISTANCE
# =============================
if not call_df.empty and not put_df.empty:
    resistance = call_df.sort_values("OI", ascending=False).iloc[0]["Strike"]
    support = put_df.sort_values("OI", ascending=False).iloc[0]["Strike"]

    c1, c2 = st.columns(2)
    c1.success(f"🟢 Support: {support}")
    c2.error(f"🔴 Resistance: {resistance}")

# =============================
# INTRADAY SIGNALS (2 HOURS + CE/PE)
# =============================
st.subheader("⏱️ Intraday Signals (Last 2 Hours)")

try:
    df = yf.download(ticker_symbol, period="1d", interval="5m", progress=False)

    if df is not None and not df.empty:

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = df.between_time("09:15", "15:30")
        df = df.tail(24)

        if "Close" in df.columns:
            df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
            df = df.dropna(subset=["Close"])

            df["EMA9"] = df["Close"].ewm(span=9).mean()
            df["EMA21"] = df["Close"].ewm(span=21).mean()

            signals = []

            for i in range(1, len(df)):
                signal = "HOLD"
                option = "-"
                strike = atm if atm else "-"

                if df["EMA9"].iloc[i] > df["EMA21"].iloc[i] and df["EMA9"].iloc[i-1] <= df["EMA21"].iloc[i-1]:
                    signal = "BUY 🚀"
                    option = "CE"

                elif df["EMA9"].iloc[i] < df["EMA21"].iloc[i] and df["EMA9"].iloc[i-1] >= df["EMA21"].iloc[i-1]:
                    signal = "SELL 🔻"
                    option = "PE"

                signals.append({
                    "Time": df.index[i].strftime("%H:%M"),
                    "Price": round(float(df["Close"].iloc[i]), 2),
                    "Signal": signal,
                    "Option": option,
                    "Strike": strike
                })

            signal_df = pd.DataFrame(signals)
            st.dataframe(signal_df, use_container_width=True)

            if not signal_df.empty:
                last = signal_df.iloc[-1]
                st.success(f"📢 Latest: {last['Signal']} | {last['Option']} | Strike: {last['Strike']}")

        else:
            st.warning("Close data missing")

    else:
        st.warning("No intraday data")

except:
    st.warning("Intraday error")

# =============================
# FOOTER
# =============================
st.caption("⚡ NSE AI PRO MAX | CE/PE + ATM + 2H Signals")
