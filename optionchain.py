import streamlit as st
import pandas as pd
import numpy as np
from streamlit_autorefresh import st_autorefresh

# =========================
# 1. AUTO REFRESH (5 MINUTES)
# =========================
st_autorefresh(interval=5 * 60 * 1000, key="manohar_ai_refresh")

# =========================
# 2. PAGE CONFIG
# =========================
st.set_page_config(page_title="Manohar AI Pro Max", layout="wide")

# =========================
# 3. TOP INDEX PRICE & TREND BAR
# =========================
st.title("🚀 MANOHAR AI PRO - TOTAL MARKET SCANNER")

# Simulated Live Data
vix_val = round(np.random.uniform(12, 18), 2)
pcr_val = round(np.random.uniform(0.6, 1.4), 2)

# Trend Logic with Buttons Style
if pcr_val > 1.1:
    trend_btn = "BULLISH 🟢"
    t_color = "success"
elif pcr_val < 0.8:
    trend_btn = "BEARISH 🔴"
    t_color = "error"
else:
    trend_btn = "SIDEWAYS 🟡"
    t_color = "warning"

# Top Metric Row 1: Index Prices
idx1, idx2, idx3, idx4 = st.columns(4)
idx1.metric("NIFTY 50", "24,510.50", "15.20")
idx2.metric("BANK NIFTY", "52,480.20", "-40.10")
idx3.metric("FIN NIFTY", "23,150.75", "5.10")
idx4.metric("MIDCAP NIFTY", "12,420.30", "22.40")

# Top Metric Row 2: Trend & VIX
st.divider()
m1, m2, m3 = st.columns(3)
with m1:
    st.write("**CURRENT TREND:**")
    if t_color == "success": st.success(trend_btn)
    elif t_color == "error": st.error(trend_btn)
    else: st.warning(trend_btn)

m2.metric("INDIA VIX", vix_val)
m3.metric("PCR RATIO", pcr_val)

st.divider()

# =========================
# 4. DATA GENERATOR & BIG MOVE LOGIC
# =========================
def get_market_analysis(index_name):
    base_prices = {"NIFTY": 24500, "BANKNIFTY": 52500, "FINNIFTY": 23100, "MIDCAPNIFTY": 12400}
    spot = base_prices[index_name]
    gap = 100 if "BANK" in index_name else 50
    
    strikes = [spot - (gap*2) + (i*gap) for i in range(5)]
    data = []
    
    for s in strikes:
        ce_oi_chg = np.random.randint(-5000, 5000)
        pe_oi_chg = np.random.randint(-5000, 5000)
        ce_vol = np.random.randint(5000, 50000)
        
        # Big Move Identification
        move = "Neutral"
        if ce_oi_chg < -3500 and ce_vol > 30000:
            move = "🚀 BIG MOVE CE"
        elif pe_oi_chg < -3500 and ce_vol > 30000:
            move = "📉 BIG MOVE PE"
            
        data.append({
            "Strike": s,
            "CE_LTP": round(np.random.uniform(50, 300), 2),
            "CE_Delta": round(np.random.uniform(0.4, 0.9), 2),
            "CE_OI_Chg": ce_oi_chg,
            "PE_LTP": round(np.random.uniform(50, 300), 2),
            "PE_Delta": round(np.random.uniform(-0.9, -0.4), 2),
            "PE_OI_Chg": pe_oi_chg,
            "Action": move
        })
    return pd.DataFrame(data)

# =========================
# 5. MAIN SCANNER TABS
# =========================
tabs = st.tabs(["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCAP"])
indices = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCAPNIFTY"]

for i, name in enumerate(indices):
    with tabs[i]:
        df = get_market_analysis(name)
        
        # Big Move Alerts Section
        big_moves = df[df['Action'] != "Neutral"]
        if not big_moves.empty:
            st.subheader("🔥 AI OBSERVATION: BIG MOVE DETECTED")
            for _, row in big_moves.iterrows():
                if "CE" in row['Action']:
                    st.success(f"**STRONGLY BUY {row['Strike']} CALL (CE)** - Short Covering Identified!")
                else:
                    st.error(f"**STRONGLY BUY {row['Strike']} PUT (PE)** - Long Unwinding Identified!")
        
        # Data Display
        st.dataframe(df.set_index('Strike'), use_container_width=True)

# =========================
# 6. SIDEBAR FOOTER
# =========================
st.sidebar.markdown(f"**Last Update:** {pd.Timestamp.now().strftime('%H:%M:%S')}")
st.sidebar.info("Next Auto-Refresh in 5 Minutes")
