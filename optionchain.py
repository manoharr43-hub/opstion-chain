import streamlit as st
import pandas as pd
import numpy as np
import requests
from streamlit_autorefresh import st_autorefresh

# =============================
# APP CONFIG
# =============================
st.set_page_config(page_title="🔥 NSE AI OPTION CHAIN PRO", layout="wide")
st.title("🔥 NSE AI OPTION CHAIN PRO DASHBOARD")

st_autorefresh(interval=20000, key="refresh")

# =============================
# INPUT
# =============================
symbol = st.text_input("Enter Symbol (NIFTY / BANKNIFTY)", "NIFTY")

# =============================
# SAFE NSE API FETCH
# =============================
def get_option_chain(symbol):
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "application/json",
        "Referer": "https://www.nseindia.com"
    }

    session = requests.Session()
    session.headers.update(headers)

    try:
        # get cookies first
        session.get("https://www.nseindia.com", timeout=5)

        response = session.get(url, timeout=10)

        if response.status_code != 200:
            return None

        data = response.json()

        if "records" not in data:
            return None

        return data

    except:
        return None

# =============================
# PROCESS DATA
# =============================
def process_data(data):
    if not data or "records" not in data:
        return pd.DataFrame()

    records = data["records"]["data"]

    rows = []

    for r in records:
        ce = r.get("CE", {})
        pe = r.get("PE", {})

        rows.append({
            "strike": r.get("strikePrice", 0),
            "ce_oi": ce.get("openInterest", 0),
            "pe_oi": pe.get("openInterest", 0),
            "ce_change": ce.get("changeinOpenInterest", 0),
            "pe_change": pe.get("changeinOpenInterest", 0),
            "ce_ltp": ce.get("lastPrice", 0),
            "pe_ltp": pe.get("lastPrice", 0),
        })

    df = pd.DataFrame(rows)

    # safety
    if df.empty:
        return df

    df["oi_diff"] = df["ce_change"] - df["pe_change"]

    return df

# =============================
# AI SIGNAL ENGINE
# =============================
def ai_signals(df):
    if df.empty:
        return df

    def signal(row):
        if row["ce_change"] > row["pe_change"] * 1.5:
            return "🔥 BUY CE"
        elif row["pe_change"] > row["ce_change"] * 1.5:
            return "🔥 BUY PE"
        else:
            return "NO TRADE"

    df["signal"] = df.apply(signal, axis=1)

    return df

# =============================
# TREND ENGINE
# =============================
def trend_engine(df):
    if df.empty:
        return "NO DATA"

    ce = df["ce_oi"].sum()
    pe = df["pe_oi"].sum()

    if ce > pe:
        return "📈 BULLISH (CE DOMINANCE)"
    else:
        return "📉 BEARISH (PE DOMINANCE)"

# =============================
# MAIN BUTTON
# =============================
if st.button("RUN AI ANALYSIS"):

    data = get_option_chain(symbol)

    if data is None:
        st.error("⚠ NSE DATA NOT AVAILABLE (BLOCKED OR NETWORK ISSUE)")
    else:
        df = process_data(data)
        df = ai_signals(df)

        st.subheader("🧠 MARKET TREND")
        st.success(trend_engine(df))

        if df.empty:
            st.warning("No data found")
        else:

            st.subheader("📊 FULL OPTION CHAIN")
            st.dataframe(df)

            # =========================
            # SIGNALS
            # =========================
            st.subheader("🚀 TOP CE SIGNALS")
            st.dataframe(df[df["signal"] == "🔥 BUY CE"].head(10))

            st.subheader("🔴 TOP PE SIGNALS")
            st.dataframe(df[df["signal"] == "🔥 BUY PE"].head(10))

            # =========================
            # BIG MOVERS
            # =========================
            st.subheader("💥 BIG MOVERS")
            st.dataframe(df.sort_values("oi_diff", ascending=False).head(10))

            st.subheader("⚡ SELL PRESSURE")
            st.dataframe(df.sort_values("oi_diff").head(10))

# =============================
# FOOTER
# =============================
st.markdown("---")
st.markdown("🔥 AI NSE OPTION CHAIN PRO | Built for intraday signals")
