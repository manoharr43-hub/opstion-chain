import streamlit as st
import pandas as pd
import requests
import time
from streamlit_autorefresh import st_autorefresh

# =========================
# 1. PAGE CONFIG & STYLING
# =========================
st.set_page_config(page_title="NSE AI PRO DASHBOARD", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #4e5d6c; }
    [data-testid="stMetricValue"] { color: #00ffcc; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 ULTRA PRO AI OPTION CHAIN DASHBOARD")

# ప్రతి 60 సెకన్లకు ఆటోమేటిక్ రీఫ్రెష్
st_autorefresh(interval=60000, key="nse_auto_update")

# =========================
# 2. NSE LIVE DATA FETCH (Handshake Logic)
# =========================
def fetch_nse_live_data(symbol):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.nseindia.com/option-chain"
    }
    
    base_url = "https://www.nseindia.com"
    api_url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"

    try:
        session = requests.Session()
        # NSE వెబ్‌సైట్‌తో కనెక్షన్ ఏర్పరచుకోవడం (Handshake)
        session.get(base_url, headers=headers, timeout=10)
        # డేటాను పొందడం
        response = session.get(api_url, headers=headers, timeout=12)
        
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

# =========================
# 3. SIDEBAR CONTROLS
# =========================
st.sidebar.header("📊 AI CONTROL PANEL")
market_index = st.sidebar.selectbox("📌 Select INDEX", ["NIFTY", "BANKNIFTY", "FINNIFTY"])
analyze_trigger = st.sidebar.button("⚡ RUN AI ANALYSIS")

# =========================
# 4. DASHBOARD MAIN LOGIC
# =========================
if analyze_trigger:
    with st.spinner(f"{market_index} లైవ్ డేటాను సేకరిస్తున్నాను..."):
        data = fetch_nse_live_data(market_index)

    if data and 'records' in data:
        # LTP (ప్రస్తుత ఇండెక్స్ ధర)
        ltp = data['records']['underlyingValue']
        st.success(f"✅ {market_index} ప్రస్తుత ధర (LTP): {ltp}")

        # Dataframe తయారీ
        raw_records = data['records']['data']
        rows = []
        for item in raw_records:
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
        # Net Flow (Put Chg - Call Chg)
        df['NET FLOW'] = df['PUT CHG'] - df['CALL CHG']

        # PCR మరియు ట్రెండ్
        total_ce_oi = df['CALL OI'].sum()
        total_pe_oi = df['PUT OI'].sum()
        pcr = round(total_pe_oi / total_ce_oi, 2) if total_ce_oi > 0 else 0

        # మెట్రిక్స్ ప్రదర్శన
        m1, m2, m3 = st.columns(3)
        m1.metric("PCR Value", pcr)
        m2.metric("Total CALL OI", f"{total_ce_oi:,}")
        m3.metric("Total PUT OI", f"{total_pe_oi:,}")

        # --- 5 COLUMN LIVE TABLE ---
        st.subheader("📊 ఆప్షన్ ఫ్లో (LIVE 5 COLUMN TABLE)")
        # ప్రస్తుతం ధర దగ్గర ఉన్న ముఖ్యమైన స్ట్రైక్స్ మాత్రమే చూపించడం
        near_ltp_df = df[(df['Strike'] >= ltp-500) & (df['Strike'] <= ltp+500)]
        st.dataframe(
            near_ltp_df[['Strike', 'CALL OI', 'CALL CHG', 'PUT OI', 'PUT CHG', 'NET FLOW']], 
            width='stretch'
        )

        # --- AI TRADE PLAN (TELUGU) ---
        st.subheader("🎯 AI ట్రేడ్ ప్లాన్ (AI TRADE PLAN)")
        
        # ట్రెండ్ నిర్ణయం
        if pcr > 1.2:
            signal = "🟢 BULLISH (CALL కొనండి)"
            logic = "మార్కెట్‌లో పుట్ రైటింగ్ ఎక్కువగా ఉంది, సపోర్ట్ బలంగా ఉంది."
        elif pcr < 0.8:
            signal = "🔴 BEARISH (PUT కొనండి)"
            logic = "మార్కెట్‌లో కాల్ రైటింగ్ ఎక్కువగా ఉంది, రెసిస్టెన్స్ బలంగా ఉంది."
        else:
            signal = "🟡 SIDEWAYS (వేచి ఉండండి)"
            logic = "మార్కెట్ ప్రస్తుతానికి ఒక రేంజ్ లో ఉంది."

        st.info(f"""
        📝 **AI విశ్లేషణ వివరాలు:**
        * **సిగ్నల్:** {signal}
        * **వివరణ:** {logic}
        * **ఎంట్రీ (Entry):** {ltp} దగ్గర
        * **స్టాప్‌లాస్ (Stoploss):** {ltp-40 if "CALL" in signal else ltp+40}
        * **టార్గెట్ (Target):** {ltp+80 if "CALL" in signal else ltp-80}
        """)

    else:
        st.error("NSE నుండి డేటా రావడం లేదు. దయచేసి 30 సెకన్లు ఆగి మళ్ళీ ప్రయత్నించండి. (NSE Server Limit)")
else:
    st.info("👈 ఎడమవైపు 'RUN AI ANALYSIS' క్లిక్ చేసి విశ్లేషణ ప్రారంభించండి.")
