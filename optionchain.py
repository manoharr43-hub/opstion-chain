import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# ==========================================
# AUTO REFRESH
# ==========================================
st_autorefresh(interval=5 * 60 * 1000, key="smart_refresh")

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(page_title="SMART AI OPTION SCANNER", layout="wide")

st.title("🚀 MANOHAR SMART AI MARKET SCANNER")

# ==========================================
# REAL INDEX DATA (YFINANCE)
# ==========================================
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
            data = yf.Ticker(symbol).history(period="1d", interval="5m")
            
            if not data.empty:
                last = data.iloc[-1]
                prev = data.iloc[-2]
                
                price = round(last["Close"], 2)
                change = round(price - prev["Close"], 2)
                volume = int(last["Volume"])
                
                result[name] = {
                    "price": price,
                    "chg": change,
                    "vol": volume
                }
            else:
                result[name] = {"price": 0, "chg": 0, "vol": 0}
        except:
            result[name] = {"price": 0, "chg": 0, "vol": 0}
    
    return result

idx_data = get_live_index()

# ==========================================
# DISPLAY INDEX
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
selected_idx = st.sidebar.selectbox(
    "SELECT INDEX",
    ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCAPNIFTY"]
)

spot_price = idx_data[selected_idx]["price"]
base_volume = idx_data[selected_idx]["vol"]

# ==========================================
# SMART OPTION DATA GENERATOR
# ==========================================
def generate_smart_data(spot, volume):
    gap = 100 if spot > 50000 else 50
    
    strikes = [int(spot - (gap*2) + (i*gap)) for i in range(5)]
    
    data = []
    
    total_call_vol = 0
    total_put_vol = 0
    
    for s in strikes:
        # Distance from spot
        dist = abs(spot - s)
        
        # Volume distribution logic
        ce_vol = int(volume * np.exp(-dist/500))
        pe_vol = int(volume * np.exp(-dist/500))
        
        # Smart OI approx
        ce_oi = ce_vol * np.random.uniform(0.8, 1.2)
        pe_oi = pe_vol * np.random.uniform(0.8, 1.2)
        
        # Price simulation
        ce_ltp = round(max(10, (spot - s) * 0.5 + np.random.uniform(10,50)), 2)
        pe_ltp = round(max(10, (s - spot) * 0.5 + np.random.uniform(10,50)), 2)
        
        total_call_vol += ce_vol
        total_put_vol += pe_vol
        
        data.append({
            "Strike": s,
            "CE_LTP": ce_ltp,
            "CE_OI": int(ce_oi),
            "PE_LTP": pe_ltp,
            "PE_OI": int(pe_oi)
        })
    
    df = pd.DataFrame(data)
    
    # PCR Calculation
    pcr = total_put_vol / total_call_vol if total_call_vol != 0 else 1
    
    return df, pcr

df, smart_pcr = generate_smart_data(spot_price, base_volume)

# ==========================================
# TREND LOGIC (SMART PCR)
# ==========================================
if smart_pcr > 1.2:
    trend = "BULLISH 🟢"
elif smart_pcr < 0.8:
    trend = "BEARISH 🔴"
else:
    trend = "SIDEWAYS 🟡"

t1, t2 = st.columns(2)
t1.metric("SMART PCR", round(smart_pcr, 2))
t2.write(f"### TREND: {trend}")

st.divider()

# ==========================================
# AI SIGNAL LOGIC (IMPROVED)
# ==========================================
st.subheader("📊 SMART AI TRADE SIGNALS")

for _, row in df.iterrows():
    
    signal = None
    
    # Smart conditions
    if row["CE_OI"] > row["PE_OI"] * 1.5:
        signal = "BUY PE"
    elif row["PE_OI"] > row["CE_OI"] * 1.5:
        signal = "BUY CE"
    
    if signal:
        if "CE" in signal:
            entry = row["CE_LTP"]
            st.success(f"{selected_idx} {row['Strike']} CE SIGNAL")
        else:
            entry = row["PE_LTP"]
            st.error(f"{selected_idx} {row['Strike']} PE SIGNAL")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("ENTRY", entry)
        c2.metric("SL", round(entry*0.8, 2))
        c3.metric("TG1", round(entry*1.2, 2))
        c4.metric("TG2", round(entry*1.5, 2))

# ==========================================
# TABLE
# ==========================================
st.write("FULL SMART DATA")
st.dataframe(df.set_index("Strike"), use_container_width=True)

# ==========================================
# FOOTER
# ==========================================
st.sidebar.markdown(
    f"Last Refresh: {pd.Timestamp.now().strftime('%H:%M:%S')}"
)
