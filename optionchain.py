import streamlit as st
import pandas as pd
import requests
import numpy as np
from streamlit_autorefresh import st_autorefresh

# =========================
# CONFIG & PAGE SETUP
# =========================
st.set_page_config(page_title="NSE AI PRO", layout="wide")

# CSS for better look
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e2130; padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 ULTRA PRO AI OPTION CHAIN DASHBOARD")

# Auto refresh every 1 minute
st_autorefresh(interval=60000, key="datarefresh")

# =========================
# LIVE NSE FETCH ENGINE
# =========================
def fetch_live_data(symbol):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com/option-chain"
    }
    
    base_url = "https://www.nseindia.com"
    api_url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"

    try:
        session = requests.Session()
        session.get(base_url, headers=headers, timeout=10)
        response = session.get(api_url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
    except:
        return None
    return None

# =========================
# SIDEBAR CONTROLS
# =========================
st.sidebar.header("📊 CONTROL PANEL")
index = st.sidebar.selectbox("📌 Select INDEX", ["NIFTY", "BANKNIFTY", "FINNIFTY"])
run_analysis = st.sidebar.button("⚡ RUN LIVE ANALYSIS")

# =========================
# MAIN DASHBOARD LOGIC
# =========================
if run_analysis:
    with st.spinner("మార్కెట్ డేటాను విశ్లేషిస్తున్నాను..."):
        data = fetch_live_data(index)

    if data and 'records' in data:
        ltp = data['records']['underlyingValue']
        st.success(f"✅ {index} లైవ్ ధర (LTP): {ltp}")

        # Data Cleaning
        raw_data = data['records']['data']
        rows = []
        for item in raw_data:
            strike = item.get('strikePrice')
            ce = item.get('CE', {})
            pe = item.get('PE', {})
            
            rows.append({
                "Strike": strike,
                "CALL OI": ce.get('openInterest', 0),
                "CALL CHG": ce.get('changeinOpenInterest', 0),
                "PUT OI": pe.get('openInterest', 0),
                "PUT CHG": pe.get('changeinOpenInterest', 0),
            })

        df = pd.DataFrame(rows)
        # Calculate Net Flow (Put Chg - Call Chg)
        df['NET FLOW'] = df['PUT CHG'] - df['CALL CHG']

        # 1. Trend Calculation (PCR)
        total_ce_oi = df['CALL OI'].sum()
        total_pe_oi = df['PUT OI'].sum()
        pcr = round(total_pe_oi / total_ce_oi, 2) if total_ce_oi > 0 else 0

        # 2. Summary Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Call OI", f"{total_ce_oi:,}")
        m2.metric("Total Put OI", f"{total_pe_oi:,}")
        m3.metric("PCR Value", pcr)

        # 3. 5 COLUMN TABLE (Main Requirement)
        st.subheader("📊 OPTION FLOW (5 COLUMN LIVE)")
        # Filter rows near current LTP
        display_df = df[(df['Strike'] >= ltp-400) & (df['Strike'] <= ltp+400)]
        st.dataframe(display_df[['Strike', 'CALL OI', 'CALL CHG', 'PUT OI', 'PUT CHG', 'NET FLOW']], use_container_width=True)

        # 4. AI TRADE PLAN (TELUGU)
        st.subheader("🎯 AI ట్రేడ్ ప్లాన్ (AI TRADE PLAN)")
        
        signal = "🟢 CALL BUY" if pcr > 1.1 else "🔴 PUT BUY" if pcr < 0.9 else "🟡 SIDEWAYS"
        color = "green" if "CALL" in signal else "red" if "PUT" in signal else "orange"

        st.markdown(f"### సిగ్నల్: <span style='color:{color}'>{signal}</span>", unsafe_allow_html=True)
        
        # AI Logic for levels
        entry = ltp
        target = ltp + 80 if "CALL" in signal else ltp - 80
        sl = ltp - 40 if "CALL" in signal else ltp + 40

        st.info(f"""
        📝 **విశ్లేషణ:**
        * **ఎంట్రీ (Entry):** {entry} దగ్గర ట్రేడ్ ప్లాన్ చేయండి.
        * **టార్గెట్ (Target):** {target} వరకు వెళ్లే అవకాశం ఉంది.
        * **స్టాప్‌లాస్ (Stoploss):** {sl} దగ్గర రిస్క్ కంట్రోల్ చేయండి.
        * **గమనిక:** PCR {pcr} ఉంది, కాబట్టి జాగ్రత్తగా ట్రేడ్ చేయండి.
        """)
    else:
        st.error("NSE సర్వర్ నుండి డేటా రావడం లేదు. దయచేసి 1 నిమిషం ఆగి 'Run Analysis' మళ్ళీ నొక్కండి.")
else:
    st.info("👈 సైడ్‌బార్‌లో ఇండెక్స్ ఎంచుకుని 'RUN LIVE ANALYSIS' క్లిక్ చేయండి.")
