import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# =========================
# AUTO REFRESH
# =========================
st_autorefresh(interval=120000, key="refresh")

st.set_page_config(page_title="STABLE AI OPTION SCANNER", layout="wide")
st.title("🚀 MANOHAR STABLE AI OPTION SCANNER (NO NSE BLOCK)")

# =========================
# LIVE INDEX DATA
# =========================
@st.cache_data(ttl=60)
def get_data():
    symbols = {
        "NIFTY": "^NSEI",
        "BANKNIFTY": "^NSEBANK"
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

c1,c2 = st.columns(2)
c1.metric("NIFTY", round(idx["NIFTY"]["price"],2), round(idx["NIFTY"]["change"],2))
c2.metric("BANKNIFTY", round(idx["BANKNIFTY"]["price"],2), round(idx["BANKNIFTY"]["change"],2))

# =========================
# SELECT INDEX
# =========================
symbol = st.sidebar.selectbox("Select Index", ["NIFTY","BANKNIFTY"])
spot = idx[symbol]["price"]
volume = idx[symbol]["vol"]

# =========================
# SMART OPTION SIMULATION
# =========================
def generate_data(spot, vol):
    gap = 100 if spot > 30000 else 50
    atm = round(spot/gap)*gap

    strikes = [atm + i*gap for i in range(-3,4)]

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
            "PE_OI": int(pe_oi)
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
st.subheader(f"Trend: {trend}")

# =========================
# ATM SIGNAL
# =========================
atm = min(df["Strike"], key=lambda x: abs(x-spot))
row = df[df["Strike"]==atm].iloc[0]

st.subheader("🔥 ATM TRADE")

col1,col2 = st.columns(2)

with col1:
    st.success(f"BUY CE {atm}")
    st.write(f"Entry: {row['CE_LTP']}")
    st.write(f"SL: {round(row['CE_LTP']*0.9,2)}")
    st.write(f"Target: {round(row['CE_LTP']*1.2,2)}")

with col2:
    st.error(f"BUY PE {atm}")
    st.write(f"Entry: {row['PE_LTP']}")
    st.write(f"SL: {round(row['PE_LTP']*0.9,2)}")
    st.write(f"Target: {round(row['PE_LTP']*1.2,2)}")

# =========================
# TABLE
# =========================
st.dataframe(df, use_container_width=True)
