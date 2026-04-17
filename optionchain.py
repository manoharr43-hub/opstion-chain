import streamlit as st
import requests
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
import time

# =============================
# CONFIG
# =============================
st.set_page_config(page_title="🔥 NSE AI PRO MAX FINAL", layout="wide")
st_autorefresh(interval=30000, key="refresh")
st.title("🚀 NSE AI SMART TRADING DASHBOARD (FINAL)")

# =============================
# OPTION CHAIN
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
                if "records" in data:
                    return data["records"]["data"]
                elif "filtered" in data:
                    return data["filtered"]["data"]
        except:
            time.sleep(1)
    return []

# =============================
# INPUT
# =============================
symbol = st.sidebar.selectbox("Select Index", ["NIFTY", "BANKNIFTY"])

# =============================
# OPTION DATA
# =============================
data = get_option_chain(symbol)

calls, puts = [], []
call_rows, put_rows = [], []

for row in data:
    ce = row.get("CE")
    pe = row.get("PE")

    if ce:
        calls.append(ce.get("openInterest", 0))
        call_rows.append({
            "Strike": ce.get("strikePrice"),
            "OI": ce.get("openInterest", 0),
            "Chg OI": ce.get("changeinOpenInterest", 0),
            "LTP": ce.get("lastPrice", 0)
        })

    if pe:
        puts.append(pe.get("openInterest", 0))
        put_rows.append({
            "Strike": pe.get("strikePrice"),
            "OI": pe.get("openInterest", 0),
            "Chg OI": pe.get("changeinOpenInterest", 0),
            "LTP": pe.get("lastPrice", 0)
        })

call_oi = sum(calls)
put_oi = sum(puts)
call_oi_change = sum([r["Chg OI"] for r in call_rows]) if call_rows else 0
put_oi_change = sum([r["Chg OI"] for r in put_rows]) if put_rows else 0

# =============================
# PCR FIX
# =============================
if call_oi > 0:
    pcr = round(put_oi / call_oi, 2)
else:
    pcr = 1.0
    st.warning("⚠️ NSE Data Issue → Using Default PCR")

bias = "SIDEWAYS"
if pcr > 1.2:
    bias = "BULLISH 🚀"
elif pcr < 0.8:
    bias = "BEARISH 🔻"

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("CALL OI", call_oi)
col2.metric("CALL OI Chg", call_oi_change)
col3.metric("PUT OI", put_oi)
col4.metric("PUT OI Chg", put_oi_change)
col5.metric("PCR", pcr)

st.info(f"📊 Market Bias: {bias}")

# =============================
# TOP STRIKES
# =============================
call_df = pd.DataFrame(call_rows)
put_df = pd.DataFrame(put_rows)

if not call_df.empty:
    st.subheader("🔥 Top CALL Strikes")
    st.dataframe(call_df.sort_values("OI", ascending=False).head(5), use_container_width=True)

if not put_df.empty:
    st.subheader("🔥 Top PUT Strikes")
    st.dataframe(put_df.sort_values("OI", ascending=False).head(5), use_container_width=True)

# =============================
# PRICE DATA
# =============================
ticker_symbol = "^NSEI" if symbol == "NIFTY" else "^NSEBANK"

df = yf.download(ticker_symbol, period="1d", interval="5m", progress=False)

if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

df.index = pd.to_datetime(df.index, errors="coerce")
df = df.between_time("09:15", "15:30")

df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
df = df.dropna(subset=["Close"])

# =============================
# ATM STRIKE
# =============================
current_price = None
atm = None

if not df.empty:
    current_price = float(df["Close"].iloc[-1])
    atm = round(current_price / 50) * 50
    st.success(f"📍 Spot: {round(current_price,2)} | 🎯 ATM: {atm}")

# =============================
# TREND
# =============================
df["EMA9"] = df["Close"].ewm(span=9).mean()
df["EMA21"] = df["Close"].ewm(span=21).mean()

trend = "SIDEWAYS"
if df["EMA9"].iloc[-1] > df["EMA21"].iloc[-1]:
    trend = "UPTREND 🚀"
else:
    trend = "DOWNTREND 🔻"

st.info(f"📊 Trend: {trend}")

# =============================
# SMART AI SIGNAL
# =============================
signal = "WAIT"

if trend == "UPTREND 🚀" and bias == "BULLISH 🚀" and put_oi_change > call_oi_change:
    signal = "🔥 STRONG CE BUY"
elif trend == "DOWNTREND 🔻" and bias == "BEARISH 🔻" and call_oi_change > put_oi_change:
    signal = "🔥 STRONG PE BUY"
elif trend == "UPTREND 🚀":
    signal = "⚡ CE BUY"
elif trend == "DOWNTREND 🔻":
    signal = "⚡ PE BUY"

st.success(f"🤖 AI Signal: {signal}")

# =============================
# INTRADAY (FULL DAY + STRIKE)
# =============================
signals = []

for i in range(1, len(df)):
    sig = "HOLD"
    opt = "-"
    strike = atm if atm else "-"

    if df["EMA9"].iloc[i] > df["EMA21"].iloc[i] and df["EMA9"].iloc[i-1] <= df["EMA21"].iloc[i-1]:
        sig = "BUY"
        opt = "CE"

    elif df["EMA9"].iloc[i] < df["EMA21"].iloc[i] and df["EMA9"].iloc[i-1] >= df["EMA21"].iloc[i-1]:
        sig = "SELL"
        opt = "PE"

    signals.append({
        "Time": df.index[i].strftime("%H:%M"),
        "Price": round(df["Close"].iloc[i], 2),
        "Signal": sig,
        "Option": opt,
        "Strike": strike
    })

st.subheader("📘 Intraday Signals (Full Day)")
st.dataframe(pd.DataFrame(signals), use_container_width=True)
