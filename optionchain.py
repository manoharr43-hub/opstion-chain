import streamlit as st
import pandas as pd
import requests
import time
from streamlit_autorefresh import st_autorefresh

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="ULTIMATE NSE AI OPTION CHAIN", layout="wide")
st.title("🔥 ULTIMATE NSE AI OPTION CHAIN (NO ERROR SYSTEM)")

st_autorefresh(interval=120000, key="refresh")  # 2 min safe refresh

# =========================
# NSE PRIMARY FETCH
# =========================
def fetch_nse(symbol):
    try:
        session = requests.Session()

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Referer": "https://www.nseindia.com/option-chain",
        }

        session.headers.update(headers)

        # warm up
        session.get("https://www.nseindia.com", timeout=10)
        time.sleep(1)

        indices = ["NIFTY", "BANKNIFTY", "FINNIFTY"]

        if symbol.upper() in indices:
            url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol.upper()}"
        else:
            url = f"https://www.nseindia.com/api/option-chain-equities?symbol={symbol.upper()}"

        res = session.get(url, timeout=10)

        if res.status_code == 200:
            return res.json()

        return None

    except:
        return None


# =========================
# FALLBACK 1: NSEPYTHON
# =========================
def fetch_nsepython(symbol):
    try:
        from nsepython import option_chain
        return option_chain(symbol.upper())
    except:
        return None


# =========================
# PROCESS DATA
# =========================
def process(data):
    if not data:
        return pd.DataFrame()

    records = data.get("records", {}).get("data", [])
    rows = []

    for r in records:
        ce = r.get("CE", {})
        pe = r.get("PE", {})

        rows.append({
            "Strike": r.get("strikePrice"),
            "Expiry": r.get("expiryDate"),
            "CE_OI": ce.get("openInterest", 0),
            "CE_CHG_OI": ce.get("changeinOpenInterest", 0),
            "CE_LTP": ce.get("lastPrice", 0),
            "PE_OI": pe.get("openInterest", 0),
            "PE_CHG_OI": pe.get("changeinOpenInterest", 0),
            "PE_LTP": pe.get("lastPrice", 0),
        })

    return pd.DataFrame(rows)


# =========================
# AI ENGINE
# =========================
def ai_engine(df):
    if df.empty:
        return df

    def sig(r):
        if r["PE_CHG_OI"] > r["CE_CHG_OI"] * 1.7:
            return "🚀 BUY"
        elif r["CE_CHG_OI"] > r["PE_CHG_OI"] * 1.7:
            return "📉 SELL"
        else:
            return "⚖️ NEUTRAL"

    df["SIGNAL"] = df.apply(sig, axis=1)
    df["DIFF"] = df["PE_CHG_OI"] - df["CE_CHG_OI"]
    return df


# =========================
# SMART FETCH (MULTI LAYER)
# =========================
def get_data(symbol):
    st.info("🔄 Trying NSE Primary API...")

    data = fetch_nse(symbol)
    if data:
        return data

    st.warning("⚠️ NSE failed, trying NSEPython...")

    data = fetch_nsepython(symbol)
    if data:
        return data

    st.error("❌ All sources failed. Try again later.")
    return None


# =========================
# UI
# =========================
symbol = st.sidebar.selectbox(
    "Select Symbol",
    ["NIFTY", "BANKNIFTY", "FINNIFTY"]
)

if st.button("🔥 GET ULTIMATE AI SIGNALS"):

    with st.spinner("Fetching live market data..."):

        raw = get_data(symbol)
        df = process(raw)

        if not df.empty:

            df = ai_engine(df)

            # =========================
            # SUMMARY
            # =========================
            ce = df["CE_OI"].sum()
            pe = df["PE_OI"].sum()
            pcr = pe / ce if ce else 0

            col1, col2, col3 = st.columns(3)
            col1.metric("CE OI", f"{ce:,}")
            col2.metric("PE OI", f"{pe:,}")
            col3.metric("PCR", round(pcr, 2))

            if pcr > 1.2:
                st.success("🔥 STRONG BULLISH MARKET")
            elif pcr < 0.8:
                st.error("📉 STRONG BEARISH MARKET")
            else:
                st.warning("⚖️ SIDEWAYS MARKET")

            # =========================
            # SIGNALS
            # =========================
            st.subheader("🔥 AI SIGNALS")
            st.dataframe(
                df[df["SIGNAL"] != "⚖️ NEUTRAL"]
                .sort_values("DIFF", ascending=False)
                .head(15)
            )

            # =========================
            # FULL DATA
            # =========================
            st.subheader("📊 FULL OPTION CHAIN")
            st.dataframe(df)

        else:
            st.error("❌ No data received from all sources")

st.markdown("---")
st.caption("⚠️ Educational purpose only. Trading involves risk.")
