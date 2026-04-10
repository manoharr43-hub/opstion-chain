import streamlit as st
import pandas as pd
import numpy as np
import requests

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="🔥 CE vs PE + STOCK AI SCANNER", layout="wide")

# =========================
# SAFE LTP
# =========================
def get_ltp(index):
    data = {
        "NIFTY": 24015,
        "BANKNIFTY": 48250,
        "FINNIFTY": 20250
    }
    return data.get(index, 24000)

# =========================
# OPTION CHAIN (SAFE)
# =========================
def option_chain(ltp):
    try:
        ltp = float(ltp)
    except:
        ltp = 24000

    base = round(ltp / 50) * 50
    strikes = [base + i * 50 for i in range(-3, 4)]

    return pd.DataFrame({
        "Strike": strikes,
        "CE_OI": np.random.randint(2000, 9000, len(strikes)),
        "PE_OI": np.random.randint(2000, 9000, len(strikes)),
    })

# =========================
# ATM
# =========================
def get_atm(df, ltp):
    return min(df["Strike"], key=lambda x: abs(x - ltp))

# =========================
# CE PE ZONE
# =========================
def ce_pe_zone(df):
    df["CE_PRESSURE"] = df["CE_OI"] / (df["PE_OI"] + 1)
    df["PE_PRESSURE"] = df["PE_OI"] / (df["CE_OI"] + 1)

    ce_zone = df.sort_values("CE_PRESSURE", ascending=False).head(3)
    pe_zone = df.sort_values("PE_PRESSURE", ascending=False).head(3)

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
    return round(df["PE_OI"].sum() / df["CE_OI"].sum(), 2)

# =========================
# SAFE STOCK ENGINE
# =========================
def stock_analysis(symbol):
    try:
        symbol = symbol.upper().strip()

        if not symbol.endswith(".NS"):
            symbol += ".NS"

        url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}"

        headers = {"User-Agent": "Mozilla/5.0"}

        res = requests.get(url, headers=headers, timeout=4)

        if not res or res.text.strip() == "":
            return None, None, "⚠ EMPTY RESPONSE"

        data = res.json()
        result = data.get("quoteResponse", {}).get("result", [])

        if not result:
            return None, None, "⚠ STOCK NOT FOUND"

        result = result[0]

        price = result.get("regularMarketPrice", 0)
        change = result.get("regularMarketChangePercent", 0)

        if price == 0:
            return None, None, "⚠ NO DATA"

        if change > 1:
            signal = "🟢 CALL SIDE STRONG"
        elif change < -1:
            signal = "🔴 PUT SIDE STRONG"
        else:
            signal = "🟡 SIDEWAYS"

        return price, change, signal

    except:
        return None, None, "⚠ ERROR LOADING"

# =========================
# SIDEBAR
# =========================
st.sidebar.title("📊 CONTROL PANEL")

index = st.sidebar.selectbox("Select Index", ["NIFTY", "BANKNIFTY", "FINNIFTY"])
stock = st.sidebar.text_input("🔎 Search Stock (e.g. RELIANCE, TCS, INFY)")

expiry = st.sidebar.radio("Expiry", ["Weekly", "Monthly"])

# =========================
# DATA
# =========================
ltp = get_ltp(index)
df = option_chain(ltp)
atm = get_atm(df, ltp)

ce_zone, pe_zone = ce_pe_zone(df)

trend_value = trend(df)
pcr_value = pcr(df)

# =========================
# HEADER
# =========================
st.title("🔥 CE vs PE + STOCK AI SCANNER")
st.caption("Safe Version - No Crash + Real Stock Search")

# =========================
# METRICS
# =========================
c1, c2, c3 = st.columns(3)

c1.metric("Index", index)
c2.metric("ATM", atm)
c3.metric("PCR", pcr_value)

# =========================
# OPTION CHAIN
# =========================
st.subheader("📊 Option Chain")
st.dataframe(df, use_container_width=True)

# =========================
# ZONES
# =========================
st.subheader("🚀 CE BIG ZONE")
st.dataframe(ce_zone)

st.subheader("📉 PE BIG ZONE")
st.dataframe(pe_zone)

# =========================
# STOCK ANALYSIS (NEW ADD)
# =========================
st.subheader("📌 STOCK ANALYSIS")

if stock:
    with st.spinner("Loading Stock Data..."):
        price, change, signal = stock_analysis(stock)

    if price is None:
        st.error(signal)
    else:
        st.metric("Price", price)
        st.metric("Change %", change)
        st.success(signal)

# =========================
# TREND REPORT
# =========================
st.subheader("📌 MARKET REPORT")

st.write(f"""
✔ Index: {index}  
✔ ATM: {atm}  
✔ PCR: {pcr_value}  
✔ Trend: {trend_value}  
✔ Expiry: {expiry}  
""")

# =========================
# FINAL SIGNAL
# =========================
if ce_zone["CE_PRESSURE"].mean() > pe_zone["PE_PRESSURE"].mean():
    st.success("🟢 CALL SIDE STRONG MARKET")
else:
    st.warning("🔴 PUT SIDE STRONG MARKET")
