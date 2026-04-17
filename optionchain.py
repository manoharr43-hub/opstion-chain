import streamlit as st
import requests
import pandas as pd
import yfinance as yf
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# =============================
# CONFIG
# =============================
st.set_page_config(page_title="🔥 NSE AI OPTION CHAIN PRO", layout="wide")
st_autorefresh(interval=20000, key="refresh")

st.title("🚀 NSE AI OPTION CHAIN + INTRADAY PRO")

# =============================
# NSE OPTION CHAIN FUNCTION
# =============================
@st.cache_data(ttl=30)
def get_option_chain(symbol):
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Referer": "https://www.nseindia.com/",
        "Accept-Language": "en-US,en;q=0.9"
    }

    session = requests.Session()

    try:
        session.get("https://www.nseindia.com", headers=headers, timeout=5)
        response = session.get(url, headers=headers, timeout=5)

        if response.status_code == 200:
            json_data = response.json()
            return json_data.get("records", {}).get("data", [])
        else:
            return []
    except:
        return []

# =============================
# USER INPUT
# =============================
symbol = st.sidebar.selectbox("Select Index", ["NIFTY", "BANKNIFTY"])

# =============================
# OPTION CHAIN PROCESS
# =============================
data = get_option_chain(symbol)

calls, puts = [], []

for item in data:
    ce = item.get("CE")
    pe = item.get("PE")

    if ce:
        calls.append({
            "Strike": ce["strikePrice"],
            "OI": ce["openInterest"],
            "Chg OI": ce["changeinOpenInterest"],
            "LTP": ce["lastPrice"]
        })

    if pe:
        puts.append({
            "Strike": pe["strikePrice"],
            "OI": pe["openInterest"],
            "Chg OI": pe["changeinOpenInterest"],
            "LTP": pe["lastPrice"]
        })

call_df = pd.DataFrame(calls)
put_df = pd.DataFrame(puts)

# =============================
# DISPLAY OPTION CHAIN
# =============================
col1, col2 = st.columns(2)

with col1:
    st.subheader(f"📈 {symbol} CALLS")
    st.dataframe(call_df, use_container_width=True)

with col2:
    st.subheader(f"📉 {symbol} PUTS")
    st.dataframe(put_df, use_container_width=True)

# =============================
# PCR + MARKET BIAS
# =============================
total_call = call_df["OI"].sum() if not call_df.empty else 0
total_put = put_df["OI"].sum() if not put_df.empty else 0

pcr = round(total_put / total_call, 2) if total_call != 0 else 0

bias = "SIDEWAYS"
if pcr > 1.2:
    bias = "BULLISH 🚀"
elif pcr < 0.8:
    bias = "BEARISH 🔻"

c1, c2 = st.columns(2)
c1.metric("PCR", pcr)
c2.metric("Market Bias", bias)

# =============================
# OI ANALYSIS (SUPPORT / RESISTANCE)
# =============================
st.subheader("📊 OI Analysis")

if not call_df.empty and not put_df.empty:
    resistance = call_df.sort_values("OI", ascending=False).iloc[0]["Strike"]
    support = put_df.sort_values("OI", ascending=False).iloc[0]["Strike"]

    col1, col2 = st.columns(2)
    col1.success(f"🟢 Strong Support: {support}")
    col2.error(f"🔴 Strong Resistance: {resistance}")

# =============================
# INTRADAY DATA
# =============================
st.subheader(f"⏱️ Intraday Signals ({symbol})")

try:
    ticker_symbol = "^NSEI" if symbol == "NIFTY" else "^NSEBANK"

    df = yf.download(
        ticker_symbol,
        period="1d",
        interval="5m",
        progress=False
    )

    if df.empty:
        st.warning("No intraday data (Market Closed)")
    else:
        df = df.between_time("09:15", "15:30")

        # Indicators
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
                "Price": round(df["Close"].iloc[i], 2),
                "EMA9": round(df["EMA9"].iloc[i], 2),
                "EMA21": round(df["EMA21"].iloc[i], 2),
                "Signal": signal
            })

        signal_df = pd.DataFrame(signals)

        st.dataframe(signal_df, use_container_width=True)

# =============================
# LIVE TREND SUMMARY
# =============================
        last = signal_df.iloc[-1]["Signal"] if not signal_df.empty else "N/A"
        st.info(f"📢 Current Signal: {last}")

except Exception as e:
    st.error(f"Error: {e}")

# =============================
# FOOTER
# =============================
st.caption("⚡ Powered by NSE + Yahoo Finance | Auto Refresh Enabled")
