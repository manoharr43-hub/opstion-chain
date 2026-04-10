import streamlit as st
import pandas as pd
import requests

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Option Chain Only", layout="wide")


# =========================
# SAFE NSE SESSION
# =========================
def get_session():
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.nseindia.com/option-chain"
    }

    session.headers.update(headers)

    try:
        session.get("https://www.nseindia.com", timeout=5)
    except:
        pass

    return session


# =========================
# FETCH OPTION CHAIN
# =========================
def fetch_option_chain(symbol):
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"

    try:
        session = get_session()
        res = session.get(url, timeout=10)

        if res.status_code == 200:
            return res.json()
        return None

    except:
        return None


# =========================
# PROCESS ONLY OPTION DATA
# =========================
def process_option_chain(data):
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
                "CE OI": ce_oi,
                "PE OI": pe_oi,
                "OI Difference": pe_oi - ce_oi,
                "Trend": "Bullish" if pe_oi > ce_oi else "Bearish"
            })

        return pd.DataFrame(result)

    except:
        return pd.DataFrame()


# =========================
# FALLBACK DATA (SAFE)
# =========================
def fallback(symbol):
    base = 22000 if symbol == "NIFTY" else 45000

    data = []
    for i in range(15):
        data.append({
            "Strike Price": base + i * 50,
            "CE OI": 1000 - i * 30,
            "PE OI": 800 + i * 40,
            "OI Difference": (800 + i * 40) - (1000 - i * 30),
            "Trend": "Bullish" if i % 2 == 0 else "Bearish"
        })

    return pd.DataFrame(data)


# =========================
# UI
# =========================
st.title("🚀 OPTION CHAIN ONLY (SAFE VERSION)")

symbol = st.selectbox("Select Index", ["NIFTY", "BANKNIFTY", "FINNIFTY"])

if st.button("RUN OPTION CHAIN"):

    st.info("Fetching option chain data...")

    raw = fetch_option_chain(symbol)
    df = process_option_chain(raw)

    # =========================
    # SAFE FALLBACK
    # =========================
    if df is None or df.empty:
        st.warning("NSE blocked → showing fallback data")
        df = fallback(symbol)

    # =========================
    # SHOW DATA
    # =========================
    st.success("Data loaded")

    st.subheader(f"{symbol} Option Chain")
    st.dataframe(df, use_container_width=True)

    # =========================
    # SIMPLE VIEW
    # =========================
    ce_total = df["CE OI"].sum()
    pe_total = df["PE OI"].sum()

    if pe_total > ce_total:
        st.markdown("### 📈 Bullish Bias")
    else:
        st.markdown("### 📉 Bearish Bias")


st.info("Educational Purpose Only")
