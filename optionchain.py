import streamlit as st
import pandas as pd
import requests
import time
from streamlit_autorefresh import st_autorefresh

# =========================
# 1. PAGE CONFIG & STYLING
# =========================
st.set_page_config(page_title="NSE AI PRO LIVE", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #4e5d6c; }
    [data-testid="stMetricValue"] { color: #00ffcc; font-size: 28px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 ULTRA PRO AI OPTION CHAIN DASHBOARD")

# --- ఎర్రర్ రాకుండా ఇక్కడ Unique Key మార్చాను ---
st_autorefresh(interval=60000, key="nse_live_unique_ref_2026_v1")

# =========================
# 2. NSE FETCH ENGINE (With Anti-Block)
# =========================
def get_nse_data(symbol):
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
        response = session.get(api_url, headers=headers, timeout=12)
        if response.status_code == 200:
            return response.json()
    except:
        return None
    return None

# =========================
# 3. SIDEBAR CONTROLS
# =========================
st.sidebar.header("📊 AI CONTROL PANEL")
market_index = st.sidebar.selectbox("📌 Select INDEX", ["NIFTY", "BANKNIFTY", "FINNIFTY"])
run_analysis = st.sidebar.button("⚡ RUN AI ANALYSIS")

# =========================
# 4. MAIN LOGIC
# =========================
if run_analysis:
    with st.spinner(f"{market_index} డేటా విశ్లేషిస్తున్నాను..."):
        data = get_nse_data(market_index)

    if data and 'records' in data:
        ltp = data['records']['underlyingValue']
        st.success(f"✅ {market_index} ప్రస్తుత ధర (LTP): {ltp}")

        # Dataframe Preparation
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
        # Net Flow Calculation
        df['NET FLOW'] = df['PUT CHG'] - df['CALL CHG']

        # PCR & Trend
        t_ce = df['CALL OI'].sum()
        t_pe = df['PUT OI'].sum()
        pcr = round(t_pe / t_ce, 2) if t_ce > 0 else 0

        # Metrics display
        col1, col2, col3 = st.columns(3)
        col1.metric("PCR Value", pcr)
        col2.metric("Total CALL OI", f"{t_ce:,}")
        col3.metric("Total PUT OI", f"{t_pe:,}")

        # --- 5 COLUMN LIVE TABLE ---
        st.subheader("📊 ఆప్షన్ ఫ్లో (LIVE 5 COLUMN TABLE)")
        display_df = df[(df['Strike'] >= ltp-500) & (df['Strike'] <= ltp+500)]
        
        # 'width=stretch' వాడాను (లాగ్ ఎర్రర్ రాకుండా)
        st.dataframe(
            display_df[['Strike', 'CALL OI', 'CALL CHG', 'PUT OI', 'PUT CHG', 'NET FLOW']], 
            width='stretch'
        )

        # --- AI TRADE PLAN (TELUGU) ---
        st.subheader("🎯 AI ట్రేడ్ ప్లాన్")
        
        if pcr > 1.2:
            signal = "🟢 BULLISH (CALL BUY)"
            desc = "మార్కెట్ లో పుట్ రైటింగ్ బలంగా ఉంది. పెరిగే అవకాశం ఉంది."
        elif pcr < 0.8:
            signal = "🔴 BEARISH (PUT BUY)"
            desc = "మార్కెట్ లో కాల్ రైటింగ్ బలంగా ఉంది. తగ్గే అవకాశం ఉంది."
        else:
            signal = "🟡 SIDEWAYS (NO TRADE)"
            desc = "మార్కెట్ ప్రస్తుతానికి రేంజ్ లో ఉంది."

        st.info(f"""
        📝 **ట్రేడ్ విశ్లేషణ:**
        * **సిగ్నల్:** {signal}
        * **వివరణ:** {desc}
        * **ఎంట్రీ:** {ltp} దగ్గర
        * **స్టాప్‌లాస్:** {ltp-40 if "CALL" in signal else ltp+40}
        * **టార్గెట్:** {ltp+80 if "CALL" in signal else ltp-80}
        """)
    else:
        st.error("NSE నుండి డేటా రావడం లేదు. దయచేసి 1 నిమిషం ఆగి మళ్ళీ ప్రయత్నించండి.")
else:
    st.info("👈 అనాలిసిస్ కోసం ఎడమవైపు ఉన్న బటన్ క్లిక్ చేయండి.")
