import streamlit as st
import requests
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
import time

# =============================
# CONFIG
# =============================
st.set_page_config(page_title="🔥 NSE AI ULTRA PRO V2 HYBRID", layout="wide")
st_autorefresh(interval=30000, key="refresh")
st.title("🚀 NSE AI ULTRA PRO V2 (HYBRID DATA ENGINE)")

# =============================
# NSE OPTION CHAIN (ROBUST)
# =============================
@st.cache_data(ttl=30)
def get_option_chain(symbol):
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"

    session = requests.Session()

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com/",
        "Connection": "keep-alive"
    }

    try:
        session.get("https://www.nseindia.com", headers=headers, timeout=10)
        res = session.get(url, headers=headers, timeout=10)

        if res.status_code == 200:
            data = res.json()
            return data.get("records", {}).get("data", [])
    except:
        return []

    return []

# =============================
# FALLBACK (DUMMY OI MODEL)
# =============================
def fallback_option_data(price):
    strikes = [price + i*50 for i in range(-5,6)]

    call_rows = []
    put_rows = []

    for s in strikes:
        call_rows.append({
            "Strike": s,
            "OI": abs(price - s) * 100,
            "Chg OI": abs(price - s) * 10,
            "LTP": max(1, price - s)
        })

        put_rows.append({
            "Strike": s,
            "OI": abs(price - s) * 100,
            "Chg OI": abs(price - s) * 10,
            "LTP": max(1, s - price)
        })

    return pd.DataFrame(call_rows), pd.DataFrame(put_rows)

# =============================
# INPUT
# =============================
symbol = st.sidebar.selectbox("Index", ["NIFTY", "BANKNIFTY"])

# =============================
# PRICE DATA
# =============================
ticker = "^NSEI" if symbol == "NIFTY" else "^NSEBANK"
df = yf.download(ticker, period="1d", interval="5m", progress=False)

if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

df = df.between_time("09:15", "15:30")
df = df.dropna()

if df.empty:
    st.error("❌ Price data not available")
    st.stop()

price = float(df["Close"].iloc[-1])
atm = round(price / 50) * 50

st.success(f"📍 Spot: {round(price,2)} | 🎯 ATM: {atm}")

# =============================
# OPTION DATA
# =============================
data = get_option_chain(symbol)

call_rows, put_rows = [], []

for row in data:
    ce = row.get("CE")
    pe = row.get("PE")

    if ce:
        call_rows.append({
            "Strike": ce.get("strikePrice"),
            "OI": ce.get("openInterest", 0),
            "Chg OI": ce.get("changeinOpenInterest", 0),
            "LTP": ce.get("lastPrice", 0)
        })

    if pe:
        put_rows.append({
            "Strike": pe.get("strikePrice"),
            "OI": pe.get("openInterest", 0),
            "Chg OI": pe.get("changeinOpenInterest", 0),
            "LTP": pe.get("lastPrice", 0)
        })

# =============================
# FALLBACK TRIGGER
# =============================
if len(call_rows) == 0 or len(put_rows) == 0:
    st.warning("⚠️ NSE blocked → Using fallback data")
    call_df, put_df = fallback_option_data(price)
else:
    call_df = pd.DataFrame(call_rows)
    put_df = pd.DataFrame(put_rows)

# =============================
# METRICS
# =============================
call_oi = call_df["OI"].sum()
put_oi = put_df["OI"].sum()

call_oi_change = call_df["Chg OI"].sum()
put_oi_change = put_df["Chg OI"].sum()

pcr = round(put_oi / call_oi, 2) if call_oi else 1

bias = "SIDEWAYS"
if pcr > 1.2:
    bias = "BULLISH 🚀"
elif pcr < 0.8:
    bias = "BEARISH 🔻"

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("CALL OI", int(call_oi))
col2.metric("CALL OI Chg", int(call_oi_change))
col3.metric("PUT OI", int(put_oi))
col4.metric("PUT OI Chg", int(put_oi_change))
col5.metric("PCR", pcr)

st.info(f"📊 Market Bias: {bias}")

# =============================
# TOP STRIKES
# =============================
st.subheader("🔥 Top CALL Strikes")
st.dataframe(call_df.sort_values("OI", ascending=False).head(5), use_container_width=True)

st.subheader("🔥 Top PUT Strikes")
st.dataframe(put_df.sort_values("OI", ascending=False).head(5), use_container_width=True)

# =============================
# INDICATORS
# =============================
df["EMA9"] = df["Close"].ewm(span=9).mean()
df["EMA21"] = df["Close"].ewm(span=21).mean()
df["VWAP"] = (df["Close"] * df["Volume"]).cumsum() / df["Volume"].cumsum()

trend = "UPTREND 🚀" if df["EMA9"].iloc[-1] > df["EMA21"].iloc[-1] else "DOWNTREND 🔻"
vwap = "ABOVE VWAP" if price > df["VWAP"].iloc[-1] else "BELOW VWAP"

st.info(f"📊 Trend: {trend} | {vwap}")

# =============================
# SIGNAL
# =============================
signal = "WAIT"

if trend == "UPTREND 🚀" and bias == "BULLISH 🚀" and price > df["VWAP"].iloc[-1]:
    signal = "💥 CE BUY"
elif trend == "DOWNTREND 🔻" and bias == "BEARISH 🔻" and price < df["VWAP"].iloc[-1]:
    signal = "💥 PE BUY"
elif trend == "UPTREND 🚀":
    signal = "⚡ CE BUY"
elif trend == "DOWNTREND 🔻":
    signal = "⚡ PE BUY"

st.success(f"🤖 AI Signal: {signal}")

# =============================
# TARGET / SL
# =============================
if "CE" in signal:
    st.success(f"🎯 Target: {round(price+50,2)} | 🛑 SL: {round(price-20,2)}")
elif "PE" in signal:
    st.success(f"🎯 Target: {round(price-50,2)} | 🛑 SL: {round(price+20,2)}")

# =============================
# INTRADAY
# =============================
signals = []

for i in range(1, len(df)):
    sig = "HOLD"
    if df["EMA9"].iloc[i] > df["EMA21"].iloc[i]:
        sig = "BUY"
    elif df["EMA9"].iloc[i] < df["EMA21"].iloc[i]:
        sig = "SELL"

    signals.append({
        "Time": df.index[i].strftime("%H:%M"),
        "Price": round(df["Close"].iloc[i], 2),
        "Signal": sig
    })

intraday_df = pd.DataFrame(signals)

st.subheader("📘 Intraday Signals")
st.dataframe(intraday_df, use_container_width=True)
