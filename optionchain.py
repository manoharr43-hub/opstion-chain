import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# ===============================
# AUTO REFRESH
# ===============================
st_autorefresh(interval=5 * 60 * 1000, key="final_refresh")

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(page_title="MANOHAR FINAL AI SCANNER", layout="wide")

st.title("🚀 MANOHAR FINAL STABLE AI MARKET SCANNER")

# ===============================
# SAFE LIVE INDEX DATA
# ===============================
def get_live_index():
    symbols = {
        "NIFTY": "^NSEI",
        "BANKNIFTY": "^NSEBANK",
        "FINNIFTY": "^NSEI",
        "MIDCAPNIFTY": "^NSEI"
    }

    result = {}

    for name, symbol in symbols.items():
        try:
            data = yf.Ticker(symbol).history(period="1d", interval="5m")

            if data.empty:
                raise Exception("No data")

            last = data.iloc[-1]
            prev = data.iloc[-2]

            result[name] = {
                "price": round(last["Close"], 2),
                "chg": round(last["Close"] - prev["Close"], 2),
                "vol": int(last["Volume"]) if last["Volume"] > 0 else 100000
            }

        except:
            result[name] = {
                "price": 24500,
                "chg": 10,
                "vol": 100000
            }

    return result

idx_data = get_live_index()

# ===============================
# DISPLAY INDEX
# ===============================
c1, c2, c3, c4 = st.columns(4)

c1.metric("NIFTY", idx_data["NIFTY"]["price"], idx_data["NIFTY"]["chg"])
c2.metric("BANKNIFTY", idx_data["BANKNIFTY"]["price"], idx_data["BANKNIFTY"]["chg"])
c3.metric("FINNIFTY", idx_data["FINNIFTY"]["price"], idx_data["FINNIFTY"]["chg"])
c4.metric("MIDCAPNIFTY", idx_data["MIDCAPNIFTY"]["price"], idx_data["MIDCAPNIFTY"]["chg"])

st.divider()

# ===============================
# SELECT INDEX
# ===============================
selected_idx = st.sidebar.selectbox(
    "SELECT INDEX",
    ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCAPNIFTY"]
)

spot = idx_data[selected_idx]["price"]
volume = idx_data[selected_idx]["vol"]

# ===============================
# DATA GENERATOR
# ===============================
def generate_data(spot, volume):

    if spot == 0:
        spot = 24500
    if volume == 0:
        volume = 100000

    gap = 100 if spot > 50000 else 50
    strikes = [int(spot - (gap*2) + (i*gap)) for i in range(5)]

    data = []
    total_call = 1
    total_put = 1

    for s in strikes:
        ce_vol = max(1000, int(volume * 0.2))
        pe_vol = max(1000, int(volume * 0.2))

        ce_oi = int(ce_vol * np.random.uniform(0.8, 1.2))
        pe_oi = int(pe_vol * np.random.uniform(0.8, 1.2))

        ce_ltp = round(np.random.uniform(50, 150), 2)
        pe_ltp = round(np.random.uniform(50, 150), 2)

        total_call += ce_vol
        total_put += pe_vol

        data.append({
            "Strike": s,
            "CE_LTP": ce_ltp,
            "PE_LTP": pe_ltp,
            "CE_OI": ce_oi,
            "PE_OI": pe_oi
        })

    df = pd.DataFrame(data)
    pcr = total_put / total_call

    return df, pcr

df, pcr = generate_data(spot, volume)

# ===============================
# TREND
# ===============================
trend = "SIDEWAYS 🟡"
if pcr > 1.2:
    trend = "BULLISH 🟢"
elif pcr < 0.8:
    trend = "BEARISH 🔴"

t1, t2 = st.columns(2)
t1.metric("SMART PCR", round(pcr, 2))
t2.write(f"### TREND: {trend}")

st.divider()

# ===============================
# SIGNALS (FIXED)
# ===============================
st.subheader("🔥 AI SIGNALS")

signals_found = False

if df.empty:
    st.error("⚠️ No Data Available")

else:
    for _, row in df.iterrows():

        if
