import streamlit as st
import requests
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
import time

# =============================
# CONFIG
# =============================
st.set_page_config(page_title="🔥 NSE AI ULTRA PRO V2", layout="wide")
st_autorefresh(interval=30000, key="refresh")
st.title("🚀 NSE AI ULTRA PRO V2 (SMART TRADING SYSTEM)")

# =============================
# NSE SESSION FIX
# =============================
session = requests.Session()
headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
}

@st.cache_data(ttl=20)
def get_option_chain(symbol):
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    try:
        session.get("https://www.nseindia.com", headers=headers, timeout=5)
        res = session.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            return res.json().get("records", {}).get("data", [])
    except:
        return []
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

call_df = pd.DataFrame(call_rows)
put_df = pd.DataFrame(put_rows)

call_oi = call_df["OI"].sum() if not call_df.empty else 0
put_oi = put_df["OI"].sum() if not put_df.empty else 0

call_oi_change = call_df["Chg OI"].sum() if not call_df.empty else 0
put_oi_change = put_df["Chg OI"].sum() if not put_df.empty else 0

# =============================
# PCR + BIAS
# =============================
pcr = round(put_oi / call_oi, 2) if call_oi else 1

if pcr > 1.2:
    bias = "BULLISH 🚀"
elif pcr < 0.8:
    bias = "BEARISH 🔻"
else:
    bias = "SIDEWAYS"

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
st.subheader("🔥 Top CALL Strikes")
st.dataframe(call_df.sort_values("OI", ascending=False).head(5), use_container_width=True)

st.subheader("🔥 Top PUT Strikes")
st.dataframe(put_df.sort_values("OI", ascending=False).head(5), use_container_width=True)

# =============================
# PRICE DATA
# =============================
ticker = "^NSEI" if symbol == "NIFTY" else "^NSEBANK"
df = yf.download(ticker, period="1d", interval="5m", progress=False)

if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

df.index = pd.to_datetime(df.index)
df = df.between_time("09:15", "15:30")
df = df.dropna()

# =============================
# INDICATORS
# =============================
df["EMA9"] = df["Close"].ewm(span=9).mean()
df["EMA21"] = df["Close"].ewm(span=21).mean()
df["VWAP"] = (df["Close"] * df["Volume"]).cumsum() / df["Volume"].cumsum()
df["Vol_Avg"] = df["Volume"].rolling(10).mean()

# =============================
# PRICE + ATM
# =============================
price = float(df["Close"].iloc[-1])
atm = round(price / 50) * 50

st.success(f"📍 Spot: {round(price,2)} | 🎯 ATM: {atm}")

# =============================
# TREND
# =============================
trend = "UPTREND 🚀" if df["EMA9"].iloc[-1] > df["EMA21"].iloc[-1] else "DOWNTREND 🔻"
vwap_status = "ABOVE VWAP" if price > df["VWAP"].iloc[-1] else "BELOW VWAP"

st.info(f"📊 Trend: {trend} | {vwap_status}")

# =============================
# VOLUME SPIKE
# =============================
volume_spike = df["Volume"].iloc[-1] > df["Vol_Avg"].iloc[-1] * 1.5

# =============================
# BREAKOUT
# =============================
high = df["High"].max()
low = df["Low"].min()

breakout = None
if price > high * 0.999:
    breakout = "🚀 BREAKOUT"
elif price < low * 1.001:
    breakout = "🔻 BREAKDOWN"

# =============================
# OI POWER
# =============================
oi_power = "NEUTRAL"
if put_oi_change > call_oi_change * 1.2:
    oi_power = "STRONG BUYERS"
elif call_oi_change > put_oi_change * 1.2:
    oi_power = "STRONG SELLERS"

st.write(f"💪 OI Power: {oi_power}")

# =============================
# FAILED SIGNAL
# =============================
failed = None
if trend == "UPTREND 🚀" and price < df["VWAP"].iloc[-1]:
    failed = "⚠️ FAILED BUY → SELL"
elif trend == "DOWNTREND 🔻" and price > df["VWAP"].iloc[-1]:
    failed = "⚠️ FAILED SELL → BUY"

if failed:
    st.error(failed)

# =============================
# FINAL SIGNAL
# =============================
signal = "WAIT"

if trend == "UPTREND 🚀" and bias == "BULLISH 🚀" and volume_spike and price > df["VWAP"].iloc[-1]:
    signal = "💥 ULTRA CE BUY"
elif trend == "DOWNTREND 🔻" and bias == "BEARISH 🔻" and volume_spike and price < df["VWAP"].iloc[-1]:
    signal = "💥 ULTRA PE BUY"
elif breakout:
    signal = breakout
elif trend == "UPTREND 🚀":
    signal = "⚡ CE BUY"
elif trend == "DOWNTREND 🔻":
    signal = "⚡ PE BUY"

st.success(f"🤖 AI Signal: {signal}")

# =============================
# TARGET / SL
# =============================
target = None
sl = None

if "CE" in signal:
    target = round(price + 50, 2)
    sl = round(price - 20, 2)
elif "PE" in signal:
    target = round(price - 50, 2)
    sl = round(price + 20, 2)

if target:
    st.success(f"🎯 Target: {target} | 🛑 SL: {sl}")

# =============================
# BEST STRIKE
# =============================
st.subheader("🎯 Smart Strike Selection")

if not call_df.empty:
    st.write("🔥 Best CE")
    st.dataframe(call_df.sort_values("Chg OI", ascending=False).head(1), use_container_width=True)

if not put_df.empty:
    st.write("🔥 Best PE")
    st.dataframe(put_df.sort_values("Chg OI", ascending=False).head(1), use_container_width=True)

# =============================
# INTRADAY SIGNALS
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
        "Option": opt,
        "Strike": atm
    })

intraday_df = pd.DataFrame(signals)

def highlight(val):
    if val == "BUY":
        return "background-color: lightgreen"
    elif val == "SELL":
        return "background-color: salmon"
    return "background-color: khaki"

st.subheader("📘 Intraday Signals")
st.dataframe(intraday_df.style.map(highlight, subset=["Signal"]), use_container_width=True)

# =============================
# TELEGRAM ALERT (OPTIONAL)
# =============================
def send_telegram(msg):
    token = "YOUR_BOT_TOKEN"
    chat_id = "YOUR_CHAT_ID"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.post(url, data={"chat_id": chat_id, "text": msg})
    except:
        pass

if "ULTRA" in signal:
    send_telegram(f"{symbol} | {signal} | Price: {price}")
