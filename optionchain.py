import streamlit as st
import requests
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
import time

# =============================
# CONFIG
# =============================
st.set_page_config(page_title="🔥 NSE AI PRO NEXT", layout="wide")
st_autorefresh(interval=20000, key="refresh")

st.title("🚀 NSE AI SMART TRADING DASHBOARD")

# =============================
# OPTION CHAIN (WITH FALLBACK)
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
# INPUT
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
        calls.append(ce.get("openInterest", 0))

    if pe:
        puts.append(pe.get("openInterest", 0))

call_oi = sum(calls)
put_oi = sum(puts)

# =============================
# PCR + AI BIAS
# =============================
if call_oi > 0:
    pcr = round(put_oi / call_oi, 2)
else:
    pcr = None

bias = "SIDEWAYS"

if pcr:
    if pcr > 1.2:
        bias = "BULLISH 🚀"
    elif pcr < 0.8:
        bias = "BEARISH 🔻"

col1, col2 = st.columns(2)

col1.metric("PCR", pcr if pcr else "N/A")
col2.metric("Market Bias", bias)

# =============================
# PRICE DATA
# =============================
ticker_symbol = "^NSEI" if symbol == "NIFTY" else "^NSEBANK"

df = yf.download(ticker_symbol, period="1d", interval="5m", progress=False)

if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

df = df.between_time("09:15", "15:30")

df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
df = df.dropna(subset=["Close"])

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
# AI SIGNAL (COMBINED)
# =============================
signal = "WAIT"

if trend == "UPTREND 🚀" and bias == "BULLISH 🚀":
    signal = "STRONG BUY CE 🚀"

elif trend == "DOWNTREND 🔻" and bias == "BEARISH 🔻":
    signal = "STRONG BUY PE 🔻"

elif trend == "UPTREND 🚀":
    signal = "BUY CE (Weak)"

elif trend == "DOWNTREND 🔻":
    signal = "BUY PE (Weak)"

st.success(f"🤖 AI Signal: {signal}")

# =============================
# INTRADAY TABLE
# =============================
signals = []

for i in range(1, len(df)):
    sig = "HOLD"
    opt = "-"

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
        "Option": opt
    })

st.dataframe(pd.DataFrame(signals), use_container_width=True)
