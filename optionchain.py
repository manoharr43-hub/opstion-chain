import streamlit as st
import pandas as pd
import requests
import time
from streamlit_autorefresh import st_autorefresh

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="ULTRA NSE AI OPTION CHAIN", layout="wide")

st.title("🔥 ULTRA NSE AI OPTION CHAIN (STABLE 2.0)")

# =========================
# AUTO REFRESH (30 Seconds)
# =========================
st_autorefresh(interval=30000, key="refresh")

# =========================
# NSE DATA FETCHER (UPDATED)
# =========================
def fetch_nse(symbol):
    try:
        # We need to hit the main page first to get cookies
        base_url = "https://www.nseindia.com"
        # Determine if it's an Index or Stock
        indices = ['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY']
        
        if symbol.upper() in indices:
            api_url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol.upper()}"
        else:
            api_url = f"https://www.nseindia.com/api/option-chain-equities?symbol={symbol.upper()}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.nseindia.com/get-quotes/derivatives?symbol=" + symbol
        }

        session = requests.Session()
        # Request home page to set cookies
        session.get(base_url, headers=headers, timeout=10)
        
        # Now request the API
        res = session.get(api_url, headers=headers, timeout=10)
        
        if res.status_code == 200:
            return res.json()
        else:
            st.error(f"NSE Error: Status Code {res.status_code}")
            return None
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return None

# =========================
# DATA PROCESSING
# =========================
def process_data(data):
    if not data or "records" not in data:
        return pd.DataFrame()

    records = data.get("records", {}).get("data", [])
    rows = []

    for r in records:
        ce = r.get("CE", {})
        pe = r.get("PE", {})
        
        # Only extract relevant strikes (near current market price usually better)
        rows.append({
            "Strike": r.get("strikePrice", 0),
            "Expiry": r.get("expiryDate"),
            "CE_OI": ce.get("openInterest", 0),
            "CE_CHG_OI": ce.get("changeinOpenInterest", 0),
            "CE_LTP": ce.get("lastPrice", 0),
            "PE_LTP": pe.get("lastPrice", 0),
            "PE_CHG_OI": pe.get("changeinOpenInterest", 0),
            "PE_OI": pe.get("openInterest", 0),
        })

    return pd.DataFrame(rows)

# =========================
# AI SIGNAL ENGINE
# =========================
def apply_ai_logic(df):
    if df.empty:
        return df

    # Calculate PCR (Put-Call Ratio) for individual strikes
    df["OI_DIFF"] = df["PE_CHG_OI"] - df["CE_CHG_OI"]
    
    def get_signal(row):
        # Bullish: PE writing (PE Change > CE Change)
        if row["PE_CHG_OI"] > row["CE_CHG_OI"] * 1.8:
            return "🚀 STRONG BUY (BULLISH)"
        # Bearish: CE writing (CE Change > PE Change)
        elif row["CE_CHG_OI"] > row["PE_CHG_OI"] * 1.8:
            return "📉 STRONG SELL (BEARISH)"
        else:
            return "⚖️ NEUTRAL"

    df["AI_SIGNAL"] = df.apply(get_signal, axis=1)
    return df

# =========================
# UI / DASHBOARD
# =========================
symbol = st.sidebar.selectbox("Select Symbol", ["NIFTY", "BANKNIFTY", "FINNIFTY", "RELIANCE", "SBIN"])

if st.button("🔄 FETCH LATEST AI SIGNALS"):
    with st.spinner("Analyzing Market Depth..."):
        raw_data = fetch_nse(symbol)
        df = process_data(raw_data)
        
        if not df.empty:
            df = apply_ai_logic(df)
            
            # Summary Metrics
            total_ce_oi = df["CE_OI"].sum()
            total_pe_oi = df["PE_OI"].sum()
            pcr = total_pe_oi / total_ce_oi if total_ce_oi != 0 else 0
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total CE OI", f"{total_ce_oi:,}")
            col2.metric("Total PE OI", f"{total_pe_oi:,}")
            col3.metric("Market PCR", round(pcr, 2))

            if pcr > 1.2:
                st.success("🎯 OVERALL MARKET SENTIMENT: VERY BULLISH")
            elif pcr < 0.8:
                st.error("🎯 OVERALL MARKET SENTIMENT: VERY BEARISH")
            else:
                st.warning("🎯 OVERALL MARKET SENTIMENT: SIDEWAYS")

            # Signal Tables
            st.subheader("🔥 Top AI Signals (Active Strikes)")
            # Filter for strikes with high activity to avoid noise
            active_signals = df[(df["AI_SIGNAL"] != "⚖️ NEUTRAL") & (df["CE_OI"] > 1000)]
            st.table(active_signals[["Strike", "AI_SIGNAL", "CE_LTP", "PE_LTP", "OI_DIFF"]].head(10))

            st.subheader("📊 Full Option Chain Analysis")
            st.dataframe(df)
        else:
            st.warning("Could not fetch data. NSE might be blocking the request or the market is closed.")

st.markdown("---")
st.caption("Note: Use this tool for educational purposes. Trading involves risk.")
