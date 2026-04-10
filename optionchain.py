import streamlit as st
import pandas as pd
import requests
import numpy as np

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="🔥 LIVE NSE AI", layout="wide")
st.title("🚀 REAL-TIME NSE AI OPTION CHAIN")

# =========================
# LIVE DATA FETCH FUNCTION
# =========================
def get_live_nse_data(symbol):
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/121.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com/"
    }
    try:
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers, timeout=10)
        response = session.get(url, headers=headers, timeout=10)
        return response.json()
    except:
        return None

# =========================
# SIDEBAR CONTROLS
# =========================
index = st.sidebar.selectbox("📌 Select INDEX", ["NIFTY", "BANKNIFTY", "FINNIFTY"])
run = st.sidebar.button("⚡ FETCH LIVE DATA")

# =========================
# MAIN LOGIC
# =========================
if run:
    data = get_live_nse_data(index)
    
    if data:
        # ప్రాథమిక వివరాలు
        ltp = data['records']['underlyingValue']
        st.success(f"📊 {index} Current Price (LTP): {ltp}")
        
        # డేటా ప్రాసెసింగ్
        raw_data = data['records']['data']
        df_list = []
        for item in raw_data:
            ce = item.get('CE', {})
            pe = item.get('PE', {})
            df_list.append({
                "Strike": item.get('strikePrice'),
                "CALL_OI": ce.get('openInterest', 0),
                "CALL_CHG": ce.get('changeinOpenInterest', 0),
                "PUT_OI": pe.get('openInterest', 0),
                "PUT_CHG": pe.get('changeinOpenInterest', 0),
            })
        
        df = pd.DataFrame(df_list)
        df['NET_FLOW'] = df['PUT_CHG'] - df['CALL_CHG']

        # 1. Trend Analysis (PCR ఆధారంగా)
        total_ce_oi = df['CALL_OI'].sum()
        total_pe_oi = df['PUT_OI'].sum()
        pcr = total_pe_oi / total_ce_oi if total_ce_oi > 0 else 0
        
        st.subheader("📊 TREND ANALYSIS")
        if pcr > 1.2:
            st.write("TREND: 🟢 BULLISH (Strong Put Writing)")
        elif pcr < 0.8:
            st.write("TREND: 🔴 BEARISH (Strong Call Writing)")
        else:
            st.write("TREND: 🟡 SIDEWAYS")

        # 2. Option Flow Table (5 Columns)
        st.subheader("📊 OPTION FLOW (LIVE 5 COLUMN)")
        st.dataframe(df[['CALL_OI', 'CALL_CHG', 'PUT_OI', 'PUT_CHG', 'NET_FLOW']].tail(15), use_container_width=True)

        # 3. AI Trade Plan
        st.subheader("🎯 AI TRADE PLAN")
        # ATM Strike ని గుర్తించడం
        atm_strike = min(df['Strike'], key=lambda x: abs(x - ltp))
        
        st.info(f"""
        🎯 ATM STRIKE: {atm_strike}
        🚦 SIGNAL: {"🟢 CALL" if pcr > 1 else "🔴 PUT"}
        🚀 ENTRY: {ltp}
        🛡️ STOPLOSS: {ltp - 50 if pcr > 1 else ltp + 50}
        📈 TARGET: {ltp + 100 if pcr > 1 else ltp - 100}
        """)
    else:
        st.error("NSE నుండి డేటా పొందలేకపోతున్నాము. దయచేసి కాసేపు ఆగి ప్రయత్నించండి.")
