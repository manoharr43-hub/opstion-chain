import streamlit as st
import pandas as pd
import requests
import time

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Ultra Pro AI Option Chain", layout="wide")


# =========================
# SAFE SESSION
# =========================
def create_session():
    session = requests.Session()

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.nseindia.com/option-chain"
    }

    session.headers.update(headers)

    try:
        session.get("https://www.nseindia.com", timeout=5)
        session.get("https://www.nseindia.com/option-chain", timeout=5)
    except:
        pass

    return session


# =========================
# FALLBACK DATA (IMPORTANT)
# =========================
def fallback_data(symbol):
    data = []
    for i in range(10):
        data.append({
            "Strike Price": 22000 + (i * 100),
            "CE Change OI": 1000 - i * 50,
            "PE Change OI": 800 + i * 60,
            "OI Difference": (800 + i * 60) - (1000 - i * 50),
            "Market Sentiment": "Bullish" if i % 2 == 0 else "Bearish"
        })
    return pd.DataFrame(data)


# =========================
# NSE FETCH (SAFE)
# =========================
def get_nse_data(symbol="NIFTY"):
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"

    try:
        session = create_session()
        response = session.get(url, timeout=10)

        if response.status_code == 200:
            return response.json()

        return None

    except:
        return None


# =========================
# PROCESS DATA SAFE
# =========================
def process_option_flow(data):
    try:
        records = data.get("filtered", {}).get("data", [])
        if not records:
            return pd.DataFrame()

        result = []

        for r in records:
            ce = r.get("CE", {})
            pe = r.get("PE", {})

            ce_oi = ce.get("changeinOpenInterest", 0)
            pe_oi = pe.get("changeinOpenInterest", 0)

            result.append({
                "Strike Price": r.get("strikePrice"),
                "CE Change OI": ce_oi,
                "PE Change OI": pe_oi,
                "OI Difference": pe_oi - ce_oi,
                "Market Sentiment": "Bullish" if pe_oi > ce_oi else "Bearish"
            })

        return pd.DataFrame(result)

    except:
        return pd.DataFrame()


# =========================
# TELUGU AI ANALYSIS
# =========================
def analysis(df):
    if df.empty:
        return "⚠️ డేటా అందుబాటులో లేదు"

    ce = df["CE Change OI"].sum()
    pe = df["PE Change OI"].sum()

    if pe > ce:
        return "📈 Bullish Market - PE dominance high"
    else:
        return "📉 Bearish Market - CE dominance high"


# =========================
# UI
# =========================
st.title("🚀 ULTRA PRO AI OPTION CHAIN (FINAL SAFE VERSION)")

symbol = st.selectbox("Select Index", ["NIFTY", "BANKNIFTY", "FINNIFTY"])

if st.button("RUN ANALYSIS"):

    with st.spinner("Fetching data safely..."):

        raw = get_nse_data(symbol)

        # =========================
        # IF NSE FAIL → USE FALLBACK
        # =========================
        if raw:
            df = process_option_flow(raw)
        else:
            st.warning("⚠️ NSE blocked - showing fallback data")
            df = fallback_data(symbol)

        # =========================
        # SHOW DATA SAFELY
        # =========================
        if df is not None and not df.empty:
            st.subheader("Option Chain Data")
            st.dataframe(df.head(20), use_container_width=True)

            st.divider()
            st.markdown("### AI Analysis")
            st.success(analysis(df))

        else:
            st.error("No data available")


st.info("Educational Purpose Only - Not Financial Advice")
