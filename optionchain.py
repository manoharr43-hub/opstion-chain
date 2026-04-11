import streamlit as st
import pandas as pd
import numpy as np

# =========================
# 1. PAGE CONFIG
# =========================
st.set_page_config(page_title="Manohar Big Move AI", layout="wide")

# =========================
# 2. TOP MARKET DASHBOARD
# =========================
st.title("🚀 MANOHAR NSE PRO - BIG MOVE IDENTIFIER")

# Simulated VIX and PCR
vix_val = round(np.random.uniform(11, 19), 2)
pcr_val = round(np.random.uniform(0.6, 1.4), 2)

c1, c2, c3, c4 = st.columns(4)
c1.metric("INDIA VIX", vix_val, delta="Big Move Soon!" if vix_val < 13 else "")
c2.metric("PCR RATIO", pcr_val)
c3.metric("NIFTY SPOT", "24,510", "15.20")
c4.metric("BANKNIFTY", "52,480", "-40.10")

st.divider()

# =========================
# 3. SMART DATA GENERATOR
# =========================
def get_big_move_data():
    indices = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCAPNIFTY"]
    all_data = []
    for name in indices:
        spot = 24500 if name == "NIFTY" else 52500
        strikes = [spot - 100, spot - 50, spot, spot + 50, spot + 100]
        
        for s in strikes:
            # Big Move Logic: OI తగ్గుతూ Volume పెరగడం
            ce_oi_chg = np.random.randint(-5000, 5000)
            ce_vol = np.random.randint(10000, 50000)
            ce_delta = round(np.random.uniform(0.4, 0.9), 2)
            
            # సిగ్నల్ ఐడెంటిఫికేషన్
            signal = "Neutral"
            if ce_oi_chg < -3000 and ce_vol > 35000: # Short Covering
                signal = "⚠️ BIG MOVE (CALL)"
            elif np.random.randint(0, 10) > 8: # Random Put Shock for Example
                signal = "⚠️ BIG MOVE (PUT)"
                
            all_data.append({
                "Index": name,
                "Strike": s,
                "LTP": round(np.random.uniform(50, 300), 2),
                "OI_Chg": ce_oi_chg,
                "Volume": ce_vol,
                "Delta": ce_delta,
                "Alert": signal
            })
    return pd.DataFrame(all_data)

# =========================
# 4. MAIN SCANNER RUN
# =========================
if st.button("🔍 START BIG MOVE SCANNING"):
    df = get_big_move_data()
    
    # ఎక్కడైనా బిగ్ మూవ్ అలర్ట్ ఉంటే పైన చూపించు
    alerts = df[df['Alert'] != "Neutral"]
    
    if not alerts.empty:
        st.warning("🔥 PRE-BREAKOUT ALERTS FOUND!")
        for _, alert in alerts.iterrows():
            with st.expander(f"ACTION REQUIRED: {alert['Index']} {alert['Strike']} {alert['Alert']}"):
                col_a, col_b = st.columns(2)
                col_a.write(f"**Reason:** OI Shock ({alert['OI_Chg']}) + High Volume ({alert['Volume']})")
                col_b.write(f"**Target Move:** 20% - 50% Quick Gains Possible")
    else:
        st.info("ప్రస్తుతానికి మార్కెట్ ప్రశాంతంగా ఉంది. పెద్ద కదలిక కోసం వేచి చూస్తున్నాం...")

    # ఇండెక్స్ వారీగా టేబుల్స్
    st.divider()
    tabs = st.tabs(["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCAPNIFTY"])
    for i, name in enumerate(["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCAPNIFTY"]):
        with tabs[i]:
            idx_df = df[df['Index'] == name].drop(columns=['Index'])
            st.dataframe(idx_df.set_index('Strike'), use_container_width=True)

# =========================
# 5. SIDEBAR GUIDE
# =========================
st.sidebar.markdown("""
### 🧠 How to Identify Big Moves:
1. **OI Shock:** OI Change నెగటివ్ (Minus) లో భారీగా ఉంటే ఆప్షన్ సెల్లర్స్ పారిపోతున్నారని అర్థం.
2. **Volume Spike:** వాల్యూమ్ అకస్మాత్తుగా పెరిగితే పెద్ద ప్లేయర్స్ ఎంటర్ అయ్యారని అర్థం.
3. **VIX Watch:** VIX 12 లోపు ఉంటే పెద్ద బ్లాస్ట్ వచ్చే అవకాశం 90% ఉంటుంది.
""")
