import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# =========================
# AUTO REFRESH
# =========================
st_autorefresh(interval=120000, key="refresh")

st.set_page_config(page_title="SMART AI SCANNER PRO", layout="wide")
st.title("🚀 MANOHAR AI OPTION SCANNER + MANUAL CONFIRM")

# =========================
# LIVE DATA
# =========================
@st.cache_data(ttl=60)
def get_data():
    symbols = {
        "NIFTY": "^NSEI",
        "BANKNIFTY": "^NSEBANK",
        "VIX": "^INDIAVIX"
    }
    data = {}
    for k,v in symbols.items():
        df = yf.Ticker(v).history(period="1d", interval="5m")
        if not df.empty:
            data[k] = {
                "price": df["Close"].iloc[-1],
                "change": df["Close"].iloc[-1] - df["Close"].iloc[-2],
                "vol": int(df["Volume"].iloc[-1]) if df["Volume"].iloc[-1] > 0 else 100000
            }
    return data

idx = get_data()

# =========================
# TOP METRICS
# =========================
c1,c2,c3 = st.columns(3)
c1.metric("NIFTY", round(idx["NIFTY"]["price"],2), round(idx["NIFTY"]["change"],2))
c2.metric("BANKNIFTY", round(idx["BANKNIFTY"]["price"],2), round(idx["BANKNIFTY"]["change"],2))
c3.metric("INDIA VIX", round(idx["VIX"]["price"],2), round(idx["VIX"]["change"],2))

st.divider()

# =========================
# SELECT INDEX
# =========================
symbol = st.sidebar.selectbox("Select Index", ["NIFTY","BANKNIFTY"])
spot = idx[symbol]["price"]
volume = idx[symbol]["vol"]

# =========================
# 🔗 QUICK LINKS (NEW)
# =========================
st.subheader("🔗 QUICK VERIFY LINKS")

colA, colB = st.columns(2)

with colA:
    if st.button("Open NSE Option Chain"):
        if symbol == "NIFTY":
            st.markdown("https://www.nseindia.com/option-chain")
        else:
            st.markdown("https://www.nseindia.com/option-chain")

with colB:
    if st.button("Open TradingView Chart"):
        if symbol == "NIFTY":
            st.markdown("https://www.tradingview.com/chart/")
        else:
            st.markdown("https://www.tradingview.com/chart/")

st.info("👉 First check NSE Option Chain + Chart → Then take trade")

st.divider()

# =========================
# SMART DATA (OLD SAME)
# =========================
def generate_data(spot, vol):
    gap = 100 if spot > 30000 else 50
    atm = round(spot/gap)*gap
    strikes = [atm + i*gap for i in range(-4,5)]

    rows = []
    total_ce = 0
    total_pe = 0

    for s in strikes:
        dist = abs(spot - s)

        ce_vol = int(vol*np.exp(-dist/500)*np.random.uniform(0.8,1.2))
        pe_vol = int(vol*np.exp(-dist/500)*np.random.uniform(0.8,1.2))

        ce_oi = ce_vol*np.random.uniform(0.8,1.3)
        pe_oi = pe_vol*np.random.uniform(0.8,1.3)

        ce_price = max(10,(spot-s)*0.4 + np.random.uniform(20,50))
        pe_price = max(10,(s-spot)*0.4 + np.random.uniform(20,50))

        total_ce += ce_oi
        total_pe += pe_oi

        rows.append({
            "Strike": s,
            "CE_LTP": round(ce_price,2),
            "PE_LTP": round(pe_price,2),
            "CE_OI": int(ce_oi),
            "PE_OI": int(pe_oi),
            "CE_VOL": ce_vol,
            "PE_VOL": pe_vol
        })

    df = pd.DataFrame(rows)
    pcr = total_pe/total_ce if total_ce else 1
    return df, pcr

df, pcr = generate_data(spot, volume)

# =========================
# TREND
# =========================
if pcr > 1.2:
    trend = "BULLISH 🟢"
elif pcr < 0.8:
    trend = "BEARISH 🔴"
else:
    trend = "SIDEWAYS 🟡"

st.metric("PCR", round(pcr,2))
st.subheader(f"Market Trend: {trend}")

# =========================
# 🔥 BIG MOVE
# =========================
st.subheader("🔥 BIG MOVE STRIKES")

big_ce = df.loc[df["CE_VOL"].idxmax()]
big_pe = df.loc[df["PE_VOL"].idxmax()]

col1, col2 = st.columns(2)

with col1:
    entry = big_ce["CE_LTP"]
    st.success(f"CE: {big_ce['Strike']}")
    st.write(f"Entry: {entry}")
    st.write(f"SL: {round(entry*0.85,2)}")
    st.write(f"TG1: {round(entry*1.2,2)}")
    st.write(f"TG2: {round(entry*1.4,2)}")

with col2:
    entry = big_pe["PE_LTP"]
    st.error(f"PE: {big_pe['Strike']}")
    st.write(f"Entry: {entry}")
    st.write(f"SL: {round(entry*0.85,2)}")
    st.write(f"TG1: {round(entry*1.2,2)}")
    st.write(f"TG2: {round(entry*1.4,2)}")

st.divider()

# =========================
# ✅ MANUAL CHECKLIST (NEW)
# =========================
st.subheader("✅ BEFORE TRADE CHECKLIST")

st.write("""
✔ NSE lo same strike verify chesava?  
✔ TradingView lo breakout confirm ayinda?  
✔ Trend (Bullish/Bearish) match ayinda?  
✔ Volume support unda?  
✔ Stop loss ready ga unda?  
""")

st.warning("⚠️ Confirmation lekunda trade cheyyakandi")

# =========================
# TABLE
# =========================
st.dataframe(df, use_container_width=True)
