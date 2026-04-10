import streamlit as st
import pandas as pd
import numpy as np
import requests
from streamlit_autorefresh import st_autorefresh

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(page_title="🔥 ULTRA NSE OPTION CHAIN AI", layout="wide")

st_autorefresh(interval=20000, key="refresh")

st.title("🔥 ULTRA NSE OPTION CHAIN AI DASHBOARD")

# =============================
# INPUT
# =============================
symbol = st.text_input("Enter Symbol (e.g. NIFTY / BANKNIFTY)", "NIFTY")
expiry = st.text_input("Expiry (e.g. 25JAN)", "25JAN")

# =============================
# MOCK / API FUNCTION (Replace with real NSE API)
# =============================
def get_option_chain(symbol):
    # Replace with real NSE endpoint if you have cookie/session
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en"
    }
    
    session = requests.Session()
    session.headers.update(headers)
    
    try:
        data = session.get(url, timeout=10).json()
        return data
    except:
        return None

# =============================
# DATA PROCESSING
# =============================
def process_data(data):
    records = data['records']['data']
    
    rows = []
    for r in records:
        if 'CE' in r or 'PE' in r:
            rows.append({
                "strike": r.get("strikePrice"),
                "ce_oi": r.get("CE", {}).get("openInterest", 0),
                "ce_change": r.get("CE", {}).get("changeinOpenInterest", 0),
                "pe_oi": r.get("PE", {}).get("openInterest", 0),
                "pe_change": r.get("PE", {}).get("changeinOpenInterest", 0),
                "ce_ltp": r.get("CE", {}).get("lastPrice", 0),
                "pe_ltp": r.get("PE", {}).get("lastPrice", 0),
            })
    
    df = pd.DataFrame(rows)
    return df

# =============================
# AI SIGNAL ENGINE
# =============================
def signal_engine(df):
    df["oi_diff"] = df["ce_change"] - df["pe_change"]
    
    def signal(row):
        if row["ce_change"] > row["pe_change"] * 1.5:
            return "🔥 CE BUY"
        elif row["pe_change"] > row["ce_change"] * 1.5:
            return "🔥 PE BUY"
        else:
            return "NO TRADE"
    
    df["signal"] = df.apply(signal, axis=1)
    
    return df

# =============================
# TREND ENGINE (SIMPLE MOCK)
# =============================
def trend_engine(df):
    ce_total = df["ce_oi"].sum()
    pe_total = df["pe_oi"].sum()
    
    if ce_total > pe_total:
        return "📈 BULLISH TREND (CE dominance)"
    else:
        return "📉 BEARISH TREND (PE dominance)"

# =============================
# MAIN
# =============================
if st.button("RUN ANALYSIS"):

    data = get_option_chain(symbol)

    if data is None:
        st.error("API error or NSE blocking request. Try again.")
    else:
        df = process_data(data)
        df = signal_engine(df)

        trend = trend_engine(df)

        st.subheader("🧠 MARKET TREND")
        st.success(trend)

        st.subheader("📊 OPTION CHAIN DATA")
        st.dataframe(df)

        # =============================
        # TOP OPPORTUNITIES
        # =============================
        st.subheader("🚀 TOP TRADING SIGNALS")

        buy_ce = df[df["signal"] == "🔥 CE BUY"].head(5)
        buy_pe = df[df["signal"] == "🔥 PE BUY"].head(5)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🔵 CE Signals")
            st.dataframe(buy_ce)

        with col2:
            st.markdown("### 🔴 PE Signals")
            st.dataframe(buy_pe)

        # =============================
        # BIG MOVERS
        # =============================
        st.subheader("💥 BIG MOVERS (OI Change)")
        df_sorted = df.sort_values("oi_diff", ascending=False)
        st.dataframe(df_sorted.head(10))

        st.subheader("⚡ BIG PE PRESSURE")
        st.dataframe(df_sorted.tail(10))
