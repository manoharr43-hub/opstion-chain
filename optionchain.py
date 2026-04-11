import streamlit as st
import pandas as pd
import numpy as np
from streamlit_autorefresh import st_autorefresh

# =========================
# 1. AUTO REFRESH (5 MINUTES)
# =========================
# 5 నిమిషాలు అంటే 5 * 60 * 1000 మిల్లీ సెకన్లు
st_autorefresh(interval=5 * 60 * 1000, key="datarefresh")

# =========================
# 2. PAGE CONFIG
# =========================
st.set_page_config(page_title="Manohar AI Auto-Scanner", layout="wide")
st.title("🚀 MANOHAR AI PRO - AUTO REFRESH SCANNER (5 Min)")

# =========================
# 3. AI OBSERVATION LOGIC (బిగ్ మూవ్ ఎలా గుర్తించాలి?)
# =========================
def ai_observation(df, name):
    observation = []
    
    # కాల్ సైడ్ అబ్జర్వేషన్ (Short Covering)
    ce_move = df[(df['CE_OI_Chg'] < -2000) & (df['CE_Delta'] > 0.6)]
    if not ce_move.empty:
        observation.append(f"🟢 AI Alert: {name} లో కాల్ రైటర్లు పారిపోతున్నారు. భారీ పెరుగుదల రావచ్చు!")
    
    # పుట్ సైడ్ అబ్జర్వేషన్ (Long Unwinding)
    pe_move = df[(df['PE_OI_Chg'] < -2000) & (abs(df['PE_Delta']) > 0.6)]
    if not pe_move.empty:
        observation.append(f"🔴 AI Alert: {name} లో పుట్ రైటర్లు పారిపోతున్నారు. మార్కెట్ పడిపోయే అవకాశం ఉంది!")
        
    return observation

# =========================
# 4. DATA GENERATOR (INDEX SPECIFIC)
# =========================
def get_data(index_name):
    base_prices = {"NIFTY": 24500, "BANKNIFTY": 52500, "FINNIFTY": 23100, "MIDCAPNIFTY": 12400}
    spot = base_prices[index_name]
    gap = 50 if index_name == "NIFTY" else 100
    
    strikes = [spot - (gap*2) + (i*gap) for i in range(5)]
    data = []
    for s in strikes:
        data.append({
            "Strike": s,
            "CE_LTP": round(np.random.uniform(50, 300), 2),
            "CE_Delta": round(np.random.uniform(0.4, 0.9), 2),
            "CE_OI_Chg": np.random.randint(-4000, 4000),
            "PE_LTP": round(np.random.uniform(50, 300), 2),
            "PE_Delta": round(np.random.uniform(-0.9, -0.4), 2),
            "PE_OI_Chg": np.random.randint(-4000, 4000)
        })
    return pd.DataFrame(data)

# =========================
# 5. DISPLAY & AI ANALYSIS
# =========================
indices = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCAPNIFTY"]
tabs = st.tabs(indices)

for i, name in enumerate(indices):
    with tabs[i]:
        df = get_data(name)
        
        # AI అబ్జర్వేషన్ చూపించడం
        obs_list = ai_observation(df, name)
        if obs_list:
            for obs in obs_list:
                st.warning(obs)
        else:
            st.info(f"AI Observation: {name} ప్రస్తుతానికి స్థిరంగా ఉంది.")

        # డేటా టేబుల్
        st.dataframe(df.set_index('Strike'), use_container_width=True)

st.sidebar.write(f"చివరిగా రిఫ్రెష్ అయిన సమయం: {pd.Timestamp.now().strftime('%H:%M:%S')}")
st.sidebar.info("ఈ పేజీ ప్రతి 5 నిమిషాలకు ఆటోమేటిక్ గా అప్‌డేట్ అవుతుంది.")
