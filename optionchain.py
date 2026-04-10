import streamlit as st
import pandas as pd
import requests
from streamlit_autorefresh import st_autorefresh

# =========================
# CONFIG & PAGE SETUP
# =========================
st.set_page_config(page_title="NSE AI PRO", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #4e5d6c; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 ULTRA PRO AI OPTION CHAIN")

# Auto refresh every 60 seconds
st_autorefresh(interval=60000, key="nse_refresh")

# =========================
# NSE FETCH ENGINE
# =========================
def fetch_nse_live(symbol):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/121.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com/option-chain"
    }
    try:
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers, timeout=10)
        url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
        response = session.get(url, headers=headers, timeout=10)
        return response.json()
    except:
        return None

# =========================
# SIDEBAR
# =========================
index = st.sidebar.selectbox("📌 Select INDEX", ["NIFTY", "BANKNIFTY", "FINNIFTY"])
run_btn = st.sidebar.button("⚡ RUN ANALYSIS")

# =========================
# MAIN CONTENT
# =========================
if run_btn:
    data = fetch_nse_live(index)
    
    if data and 'records' in data:
        ltp = data['records']['underlyingValue']
        st.success(f"📊 {index} LTP: {ltp}")

        # Data Frame Preparation
        raw_list = data['records']['data']
        rows = []
        for item in raw_list:
            ce = item.get('CE', {})
            pe = item.get('PE', {})
            rows.append({
                "Strike": item.get('strikePrice'),
                "CALL OI": ce.get('openInterest', 0),
                "CALL CHG": ce.get('changeinOpenInterest', 0),
                "PUT OI": pe.get('openInterest', 0),
                "PUT CHG": pe.get('changeinOpenInterest', 0),
            })
        
        df = pd.DataFrame(rows)
        df['NET FLOW'] = df['PUT CHG'] - df['CALL CHG']

        # TREND & PCR
        total_ce = df['CALL OI'].sum()
        total_pe = df['PUT OI'].sum()
        pcr = round(total_pe / total_ce, 2) if total_ce > 0 else 0

        c1, c2, c3 = st.columns(3)
        c1.metric("PCR", pcr)
        c2.metric("Total Call OI", f"{total_ce:,}")
        c3.metric("Total Put OI", f"{total_pe:,}")

        # 5 COLUMN TABLE (Updated width parameter)
        st.subheader("📊 ఆప్షన్ ఫ్లో (LIVE 5 COLUMN)")
        display_df = df[(df['Strike'] >= ltp-500) & (df['Strike'] <= ltp+500)]
        
        # ఇక్కడ width='stretch' వాడాను, ఇది మీ లాగ్‌లో ఉన్న ఎర్రర్‌ను పోగొడుతుంది
        st.dataframe(display_df[['Strike', 'CALL OI', 'CALL CHG', 'PUT OI', 'PUT CHG', 'NET FLOW']], width='stretch')

        # AI TRADE PLAN (TELUGU)
        st.subheader("🎯 AI ట్రేడ్ ప్లాన్")
        signal = "🟢 CALL BUY" if pcr > 1.1 else "🔴 PUT BUY" if pcr < 0.9 else "🟡 SIDEWAYS"
        
        st.info(f"""
        📝 **వివరాలు:**
        * **సిగ్నల్:** {signal}
        * **ఎంట్రీ:** {ltp}
        * **స్టాప్‌లాస్:** {ltp-50 if "CALL" in signal else ltp+50}
        * **టార్గెట్:** {ltp+100 if "CALL" in signal else ltp-100}
        """)
    else:
        st.error("NSE నుండి డేటా రావడం లేదు. దయచేసి కాసేపు ఆగి మళ్ళీ ప్రయత్నించండి.")
