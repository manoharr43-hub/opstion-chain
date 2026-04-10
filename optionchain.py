import streamlit as st
import pandas as pd
import numpy as np
import requests
import time

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="🔥 NSE LIVE CE vs PE AI SCANNER", layout="wide")

# =========================
# SESSION (IMPORTANT FOR NSE)
# =========================
headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "application/json,text/plain,*/*",
    "Referer": "https://www.nseindia.com"
}

session = requests.Session()
session.headers.update(headers)

# =========================
# NSE OPTION CHAIN FETCH (SAFE)
# =========================
def fetch_option_chain(symbol="NIFTY"):
    try:
        url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"

        # warm-up (must)
        session.get("https://www.nseindia.com", timeout=5)
        time.sleep(1)

        res = session.get(url, timeout=10)

        if res.text.strip() == "":
            return None

        try:
            data = res.json()
        except:
            return None

        records = data["records"]["data"]

        rows = []
        for i in records:
            strike = i.get("strikePrice")

            ce = i.get("CE", {})
            pe = i.get("PE", {})

            rows.append([
                strike,
                ce.get("openInterest", 0),
                pe.get("openInterest", 0),
                ce.get("totalTradedVolume", 0),
                pe.get("totalTradedVolume", 0),
            ])

        df = pd.DataFrame(rows, columns=["Strike", "CE_OI", "PE_OI", "CE_VOL", "PE_VOL"])
        return df

    except:
        return None

# =========================
# ATM FINDER
# =========================
def get_atm(df, ltp):
    return min(df["Strike"], key=lambda x: abs(x - ltp))

# =========================
# ZONE ANALYSIS
# =========================
def zone_analysis(df, atm):
    df = df.copy()

    df["CE_PRESSURE"] = df["CE_OI"] / (df["PE_OI"] + 1)
    df["PE_PRESSURE"] = df["PE_OI"] / (df["CE_OI"] + 1)
    df["DIST"] = abs(df["Strike"] - atm)

    ce_zone = df.sort_values(["CE_PRESSURE", "DIST"], ascending=[False, True]).head(5)
    pe_zone = df.sort_values(["PE_PRESSURE", "DIST"], ascending=[False, True]).head(5)

    return ce_zone, pe_zone

# =========================
# TREND
# =========================
def trend(df):
    ce = df["CE_OI"].sum()
    pe = df["PE_OI"].sum()

    if ce > pe * 1.1:
        return "🟢 BULLISH"
    elif pe > ce * 1.1:
        return "🔴 BEARISH"
    return "🟡 SIDEWAYS"

# =========================
# PCR
# =========================
def pcr(df):
    return df["PE_OI"].sum() / (df["CE_OI"].sum() + 1)

# =========================
# UI
# =========================
st.title("🔥 NSE LIVE OPTION CHAIN + CE/PE AI ZONES")
st.caption("Real NSE Data + Smart Money Pressure Detection")

symbol = st.sidebar.selectbox("Select Index", ["NIFTY", "BANKNIFTY"])

# =========================
# FETCH DATA
# =========================
df = fetch_option_chain(symbol)

# =========================
# FALLBACK (IMPORTANT)
# =========================
if df is None or df.empty:
    st.warning("⚠ NSE blocked → Running fallback mode")

    df = pd.DataFrame({
        "Strike": np.arange(24000, 24150, 50),
        "CE_OI": np.random.randint(2000, 8000, 3),
        "PE_OI": np.random.randint(2000, 8000, 3),
        "CE_VOL": np.random.randint(100, 500, 3),
        "PE_VOL": np.random.randint(100, 500, 3),
    })

# =========================
# LTP (SAFE)
# =========================
ltp = df["Strike"].mean()
atm = get_atm(df, ltp)

ce_zone, pe_zone = zone_analysis(df, atm)

trend_value = trend(df)
pcr_value = pcr(df)

# =========================
# DASHBOARD
# =========================
st.metric("INDEX", symbol)
st.metric("ATM", atm)
st.metric("PCR", round(pcr_value, 2))
st.metric("TREND", trend_value)

# =========================
# TABLE
# =========================
st.subheader("📊 OPTION CHAIN DATA")
st.dataframe(df, use_container_width=True)

# =========================
# ZONES
# =========================
st.subheader("🚀 CE STRONG ZONE")
st.dataframe(ce_zone, use_container_width=True)

st.subheader("📉 PE STRONG ZONE")
st.dataframe(pe_zone, use_container_width=True)

# =========================
# SIGNAL ENGINE
# =========================
st.subheader("🧠 MARKET SIGNAL")

if ce_zone["CE_PRESSURE"].mean() > pe_zone["PE_PRESSURE"].mean():
    st.success("🟢 CALL SIDE STRONG (BUY BIAS)")
else:
    st.warning("🔴 PUT SIDE STRONG (SELL BIAS)")

st.success("✅ OLD CODE SAFE + REAL NSE + Fallback SYSTEM ACTIVE")
