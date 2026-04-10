import streamlit as st
import pandas as pd
import requests
import time

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Ultra Safe Option Chain", layout="wide")


# =========================
# SAFE SESSION
# =========================
def create_session():
    session = requests.Session()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.nseindia.com/option-chain"
    }

    session.headers.update(headers)

    try:
        session.get("https://www.nseindia.com", timeout=5)
        time.sleep(1)
    except:
        pass

    return session


# =========================
# FETCH NSE DATA
# =========================
def fetch_option_chain(symbol):
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"

    try:
        session = create_session()
        res = session.get(url, timeout=10)

        if res.status_code == 200:
            return res.json()

        return None

    except:
        return None


# =========================
# PROCESS DATA SAFE
# =========================
def process_data(data):
    try:
        records = data.get("filtered", {}).get("data", [])
        if not records:
            return pd.DataFrame()

        out = []

        for r in records:
            ce = r.get("CE", {})
            pe = r.get("PE", {})

            ce_oi = ce.get("changeinOpenInterest", 0)
            pe_oi = pe.get("changeinOpenInterest", 0)

            out.append({
                "Strike Price": r.get("strikePrice"),
                "CE OI": ce_oi,
                "PE OI": pe_oi,
                "OI Diff": pe_oi - ce_oi,
                "Trend": "Bullish" if pe_oi > ce_oi else "Bearish"
            })

        return pd.DataFrame(out)

    except:
        return pd.DataFrame()


# =========================
# FALLBACK DATA (ALWAYS SAFE)
# =========================
def fallback(symbol):
    base = 22000 if symbol == "NIFTY" else 45000

    data = []
    for i in range(20):
        data.append({
            "Strike Price": base + i * 50,
            "CE OI": 1000 - i * 25,
            "PE OI": 800 + i * 35,
            "OI Diff": (800 + i * 35) - (1000 - i * 25),
            "Trend": "Bullish" if i % 2 == 0 else "Bearish"
        })

    return pd.DataFrame(data)


# =========================
# UI
# =========================
st.title("🚀 ULTRA SAFE OPTION CHAIN (FINAL VERSION)")

symbol = st.selectbox("Select Index", ["NIFTY", "BANKNIFTY", "FINNIFTY"])

if st.button("RUN ANALYSIS"):

    st.info("Fetching option chain safely...")

    raw = fetch_option_chain(symbol)
    df = process_data(raw)

    # =========================
    # SAFE FALLBACK LOGIC
    # =========================
    if df is None or df.empty:
        st.warning("⚠️ NSE blocked or empty response → fallback data loaded")
        df = fallback(symbol)

    # =========================
    # SHOW DATA (ALWAYS)
    # =========================
    st.success("Data ready")

    st.subheader(f"{symbol} Option Chain Data")
    st.dataframe(df, use_container_width=True)

    st.divider()

    # =========================
    # SIMPLE ANALYSIS
    # =========================
    ce_total = df["CE OI"].sum()
    pe_total = df["PE OI"].sum()

    if pe_total > ce_total:
        st.markdown("### 📈 Market Bias: BULLISH")
    else:
        st.markdown("### 📉 Market Bias: BEARISH")


st.info("Educational Purpose Only - Not Financial Advice")
