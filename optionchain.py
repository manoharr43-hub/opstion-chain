import streamlit as st
import pandas as pd
import numpy as np
from streamlit_autorefresh import st_autorefresh

# ==========================================
# 1. AUTO REFRESH (5 MINUTES)
# ==========================================
st_autorefresh(interval=5 * 60 * 1000, key="manohar_pro_refresh")

# ==========================================
# 2. PAGE CONFIG
# ==========================================
st.set_page_config(page_title="Manohar AI Market Scanner", layout="wide")

# ==========================================
# 3. TOP INDEX PRICE DISPLAY
# ==========================================
st.title("🚀 MANOHAR NSE PRO - SMART SCANNER")

# ఇండెక్స్ వారీగా ఫిక్స్‌డ్ డేటా (Simulated for UI)
idx_prices = {
    "NIFTY": {"price": "24,510.50", "chg": "15.20"},
    "BANKNIFTY": {"price": "52,480.20", "chg": "-40.10"},
    "FINNIFTY": {"price": "23,150.75", "chg": "5.10"},
    "MIDCAPNIFTY": {"price": "12,420.30", "chg": "22.40"}
}

c1, c2, c3, c4 = st.columns(4)
c1.metric("NIFTY 50", idx_prices["NIFTY"]["price"], idx_prices["NIFTY"]["chg"])
c2.metric("BANK NIFTY", idx_prices["BANKNIFTY"]["price"], idx_prices["BANKNIFTY"]["chg"])
c3.metric("FIN NIFTY", idx_prices["FINNIFTY"]["price"], idx_prices["FINNIFTY"]["chg"])
c4.metric("MIDCAP NIFTY", idx_prices["MIDCAPNIFTY"]["price"], idx_prices["MIDCAPNIFTY"]["chg"])

st.divider()

# ==========================================
# 4. DYNAMIC INDEX & PCR SELECTION
# ==========================================
# ఇక్కడ ఇండెక్స్ మారినప్పుడు PCR మరియు VIX మారేలా లాజిక్
selected_idx = st.sidebar.selectbox("🎯 SELECT INDEX TO SCAN", ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCAPNIFTY"])

# ఇండెక్స్ ని బట్టి వేర్వేరు PCR విలువలు
pcr_values = {"NIFTY": 1.15, "BANKNIFTY": 0.75, "FINNIFTY": 0.95, "MIDCAPNIFTY": 1.30}
current_pcr = pcr_values[selected_idx]
vix_val = 14.20

# Trend Logic
if current_pcr > 1.1: trend_text, t_color = "BULLISH 🟢", "success"
elif current_pcr < 0.8: trend_text, t_color = "BEARISH 🔴", "error"
else: trend_text, t_color = "SIDEWAYS 🟡", "warning"

m1, m2, m3 = st.columns(3)
with m1:
    st.write(f"**{selected_idx} TREND:**")
    if t_color == "success": st.success(trend_text)
    elif t_color == "error": st.error(trend_text)
    else: st.warning(trend_text)

m2.metric("INDIA VIX", vix_val)
m3.metric(f"{selected_idx} PCR", current_pcr)

st.divider()

# ==========================================
# 5. DATA GENERATOR & AI SIGNAL LOGIC
# ==========================================
def get_signals(index_name):
    base = {"NIFTY": 24500, "BANKNIFTY": 52500, "FINNIFTY": 23100, "MIDCAPNIFTY": 12400}
    spot = base[index_name]
    gap = 100 if "BANK" in index_name else 50
    strikes = [spot - (gap*2) + (i*gap) for i in range(5)]
    
    data = []
    for s in strikes:
        ce_oi_chg = np.random.randint(-5000, 5000)
        pe_oi_chg = np.random.randint(-5000, 5000)
        ce_ltp = round(np.random.uniform(100, 300), 2)
        pe_ltp = round(np.random.uniform(100, 300), 2)
        
        # AI Analysis for Entry
        signal = "Neutral"
        if ce_oi_chg < -3500: signal = "STRONG BUY CE"
        elif pe_oi_chg < -3500: signal = "STRONG BUY PE"
            
        data.append({
            "Strike": s, "CE_LTP": ce_ltp, "CE_OI_Chg": ce_oi_chg,
            "PE_LTP": pe_ltp, "PE_OI_Chg": pe_oi_chg, "AI_Signal": signal
        })
    return pd.DataFrame(data)

# ==========================================
# 6. SIGNAL DISPLAY (ENTRY, SL, TG1, TG2)
# ==========================================
df = get_signals(selected_idx)
st.subheader(f"📊 AI ANALYSIS & TRADE SIGNALS: {selected_idx}")

# సిగ్నల్స్ ని విడిగా చూపించడం
signals = df[df['AI_Signal'] != "Neutral"]
if not signals.empty:
    for _, row in signals.iterrows():
        if "CE" in row['AI_Signal']:
            entry = row['CE_LTP']
            with st.container():
                st.success(f"🔥 **{selected_idx} {row['Strike']} CALL (CE) - BIG MOVE DETECTED**")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("ENTRY", f"₹{entry}")
                c2.metric("STOP LOSS", f"₹{round(entry*0.80, 2)}", delta="-20%")
                c3.metric("TARGET 1 (TG1)", f"₹{round(entry*1.20, 2)}", delta="20%")
                c4.metric("TARGET 2 (TG2)", f"₹{round(entry*1.50, 2)}", delta="50%")
        else:
            entry = row['PE_LTP']
            with st.container():
                st.error(f"📉 **{selected_idx} {row['Strike']} PUT (PE) - BIG MOVE DETECTED**")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("ENTRY", f"₹{entry}")
                c2.metric("STOP LOSS", f"₹{round(entry*0.80, 2)}", delta="-20%")
                c3.metric("TARGET 1 (TG1)", f"₹{round(entry*1.20, 2)}", delta="20%")
                c4.metric("TARGET 2 (TG2)", f"₹{round(entry*1.50, 2)}", delta="50%")

st.divider()
st.write("**FULL DATA TABLE:**")
st.dataframe(df.set_index('Strike'), use_container_width=True)

# Footer
st.sidebar.markdown(f"**Last AI Refresh:** {pd.Timestamp.now().strftime('%H:%M:%S')}")
