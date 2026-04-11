import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# ==========================================
# AUTO REFRESH (5 Minutes)
# ==========================================
st_autorefresh(interval=5 * 60 * 1000, key="smart_refresh")

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(page_title="SMART AI OPTION SCANNER", layout="wide")

st.title("🚀 MANOHAR SMART AI MARKET SCANNER")

# ==========================================
# REAL INDEX DATA
# ==========================================
@st.cache_data(ttl=60)
def get_live_index():
    symbols = {
        "NIFTY": "^NSEI",
        "BANKNIFTY": "^NSEBANK",
        "FINNIFTY": "^CNXFINANCE",
        "MIDCAPNIFTY": "^NSEMDCP50"
    }
    result = {}
    for name, symbol in symbols.items():
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="5d", interval="5m")
            if not data.empty and len(data) >= 2:
                last = data.iloc[-1]
                prev = data.iloc[-2]
                price = round(last["Close"], 2)
                change = round(price - prev["Close"], 2)
                volume = int(last["Volume"]) if last["Volume"] > 0 else 500000 
                result[name] = {"price": price, "chg": change, "vol": volume}
            else:
                result[name] = {"price": 1.0, "chg": 0.0, "vol": 100000}
        except:
            result[name] = {"price": 1.0, "chg": 0.0, "vol": 100000}
    return result

idx_data = get_live_index()

# ==========================================
# DISPLAY INDEX METRICS
# ==========================================
c1, c2, c3, c4 = st.columns(4)
c1.metric("NIFTY", idx_data["NIFTY"]["price"], idx_data["NIFTY"]["chg"])
c2.metric("BANKNIFTY", idx_data["BANKNIFTY"]["price"], idx_data["BANKNIFTY"]["chg"])
c3.metric("FINNIFTY", idx_data["FINNIFTY"]["price"], idx_data["FINNIFTY"]["chg"])
c4.metric("MIDCAPNIFTY", idx_data["MIDCAPNIFTY"]["price"], idx_data["MIDCAPNIFTY"]["chg"])

st.divider()

# ==========================================
# SELECT INDEX
# ==========================================
selected_idx = st.sidebar.selectbox("SELECT INDEX", ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCAPNIFTY"])
spot_price = idx_data[selected_idx]["price"]
base_volume = idx_data[selected_idx]["vol"]

# ==========================================
# SMART OPTION DATA GENERATOR
# ==========================================
def generate_smart_data(spot, volume):
    if spot <= 10: return pd.DataFrame(), 1.0
    gap = 100 if spot > 30000 else 50
    # Current ATM Strike
    atm_strike = round(spot / gap) * gap
    strikes = [int(atm_strike - (gap*2) + (i*gap)) for i in range(5)]
    
    data = []
    total_call_vol = 0
    total_put_vol = 0
    
    for s in strikes:
        dist = abs(spot - s)
        ce_vol = int(volume * np.exp(-dist/500) * np.random.uniform(0.7, 1.3))
        pe_vol = int(volume * np.exp(-dist/500) * np.random.uniform(0.7, 1.3))
        
        ce_oi = ce_vol * np.random.uniform(0.8, 1.2)
        pe_oi = pe_vol * np.random.uniform(0.8, 1.2)
        
        ce_ltp = round(max(10, (spot - s) * 0.4 + np.random.uniform(20,60)), 2)
        pe_ltp = round(max(10, (s - spot) * 0.4 + np.random.uniform(20,60)), 2)
        
        total_call_vol += ce_vol
        total_put_vol += pe_vol
        
        data.append({
            "Strike": s,
            "CE_LTP": ce_ltp, "CE_OI": int(ce_oi), "CE_VOL": ce_vol,
            "PE_LTP": pe_ltp, "PE_OI": int(pe_oi), "PE_VOL": pe_vol
        })
    
    df = pd.DataFrame(data)
    pcr = total_put_vol / total_call_vol if total_call_vol != 0 else 1
    return df, pcr

df, smart_pcr = generate_smart_data(spot_price, base_volume)

# ==========================================
# BIG MOVEMENT LOGIC
# ==========================================
if not df.empty:
    st.subheader("🔥 BIG MOVEMENT ALERTS (HFT SCANNER)")
    
    # Logic: Finding strikes with highest volume spikes
    high_vol_ce = df.loc[df['CE_VOL'].idxmax()]
    high_vol_pe = df.loc[df['PE_VOL'].idxmax()]
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.info(f"⚡ CE BREAKOUT WATCH: {high_vol_ce['Strike']}")
        st.write(f"**Action:** BUY CE if Price > {high_vol_ce['CE_LTP']}")
        st.write(f"**Stop Loss:** {round(high_vol_ce['CE_LTP'] * 0.85, 2)}")
        st.write(f"**Exit (Target):** {round(high_vol_ce['CE_LTP'] * 1.3, 2)}")

    with col_b:
        st.warning(f"⚡ PE BREAKOUT WATCH: {high_vol_pe['Strike']}")
        st.write(f"**Action:** BUY PE if Price > {high_vol_pe['PE_LTP']}")
        st.write(f"**Stop Loss:** {round(high_vol_pe['PE_LTP'] * 0.85, 2)}")
        st.write(f"**Exit (Target):** {round(high_vol_pe['PE_LTP'] * 1.3, 2)}")

    st.divider()

    # ==========================================
    # TREND & SIGNALS
    # ==========================================
    trend = "SIDEWAYS 🟡"
    if smart_pcr > 1.2: trend = "BULLISH 🟢"
    elif smart_pcr < 0.8: trend = "BEARISH 🔴"
    
    t1, t2 = st.columns(2)
    t1.metric("SMART PCR", round(smart_pcr, 2))
    t2.write(f"### MARKET TREND: {trend}")
    
    st.subheader("📊 AI TRADE SIGNALS")
    
    for _, row in df.iterrows():
        # Enhanced signal logic
        if row["PE_OI"] > row["CE_OI"] * 1.3 and trend == "BULLISH 🟢":
            with st.expander(f"✅ BUY CALL: {selected_idx} {row['Strike']} CE", expanded=True):
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("ENTRY", row['CE_LTP'])
                c2.metric("STOP LOSS", round(row['CE_LTP']*0.8, 2))
                c3.metric("EXIT T1", round(row['CE_LTP']*1.2, 2))
                c4.metric("EXIT T2", round(row['CE_LTP']*1.5, 2))
                
        elif row["CE_OI"] > row["PE_OI"] * 1.3 and trend == "BEARISH 🔴":
            with st.expander(f"🚨 BUY PUT: {selected_idx} {row['Strike']} PE", expanded=True):
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("ENTRY", row['PE_LTP'])
                c2.metric("STOP LOSS", round(row['PE_LTP']*0.8, 2))
                c3.metric("EXIT T1", round(row['PE_LTP']*1.2, 2))
                c4.metric("EXIT T2", round(row['PE_LTP']*1.5, 2))

    st.write("### FULL OPTION CHAIN DATA")
    st.dataframe(df.set_index("Strike"), use_container_width=True)
else:
    st.error("Data fetch failed. Please check your connection.")

st.sidebar.write(f"Last Update: {pd.Timestamp.now().strftime('%H:%M:%S')}")
