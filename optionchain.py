import streamlit as st
import pandas as pd
import requests
import time

# --- Page Configuration ---
st.set_page_config(page_title="Ultra Pro AI Option Chain", layout="wide")

# --- Enhanced NSE API Fetching Logic ---
# ఈ సెక్షన్ డేటాని NSE నుండి సురక్షితంగా తెస్తుంది
def get_nse_data(symbol="NIFTY"):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.nseindia.com/option-chain'
    }
    
    base_url = "https://www.nseindia.com"
    api_url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    
    session = requests.Session()
    try:
        # మొదట మెయిన్ సైట్ ని విజిట్ చేసి కుకీస్ ని సెట్ చేయాలి
        session.get(base_url, headers=headers, timeout=10)
        # ఇప్పుడు అసలు డేటా కోసం రిక్వెస్ట్ పంపాలి
        response = session.get(api_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

# --- Process Data for 5-Column Option Flow ---
def process_option_flow(data):
    try:
        records = data['filtered']['data']
        flow_list = []
        
        for entry in records:
            strike_price = entry['strikePrice']
            if 'CE' in entry and 'PE' in entry:
                ce_oi = entry['CE']['changeinOpenInterest']
                pe_oi = entry['PE']['changeinOpenInterest']
                
                # OI Difference మరియు Sentiment లెక్కించడం
                oi_diff = pe_oi - ce_oi
                sentiment = "Bullish" if oi_diff > 0 else "Bearish"
                
                flow_list.append({
                    "Strike Price": strike_price,
                    "CE Change in OI": ce_oi,
                    "PE Change in OI": pe_oi,
                    "OI Difference": oi_diff,
                    "Market Sentiment": sentiment
                })
        return pd.DataFrame(flow_list)
    except Exception:
        return pd.DataFrame()

# --- Telugu AI Analysis Generator ---
def generate_telugu_analysis(df):
    if df.empty:
        return "విశ్లేషణకు తగినంత డేటా లేదు."
        
    total_ce_oi = df["CE Change in OI"].sum()
    total_pe_oi = df["PE Change in OI"].sum()
    
    if total_pe_oi > total_ce_oi:
        trend = "బుల్లిష్ (Bullish) - మార్కెట్ పెరిగే అవకాశం ఉంది."
        strategy = "సపోర్ట్ లెవెల్స్ (PE OI అధికంగా ఉన్న చోట) గమనిస్తూ ఉండండి."
    else:
        trend = "బేరిష్ (Bearish) - మార్కెట్ తగ్గే అవకాశం ఉంది."
        strategy = "రెసిస్టెన్స్ లెవెల్స్ (CE OI అధికంగా ఉన్న చోట) గమనిస్తూ ఉండండి."
        
    return f"""
    ### 📊 AI మార్కెట్ విశ్లేషణ (Telugu)
    - **ప్రస్తుత ట్రెండ్:** {trend}
    - **ముఖ్య గమనిక:** PE Change in OI ఎక్కువగా ఉంటే మార్కెట్ పైకి వెళ్లే ఛాన్స్ ఉంది.
    - **ట్రేడ్ ప్లాన్:** {strategy}
    """

# --- UI Layout ---
st.title("🚀 ULTRA PRO AI OPTION CHAIN")

with st.sidebar:
    st.header("📌 Select INDEX")
    symbol = st.selectbox("Index ఎంచుకోండి", ["NIFTY", "BANKNIFTY", "FINNIFTY"])
    run_btn = st.button("RUN ANALYSIS")

if run_btn:
    with st.spinner('డేటాను సేకరిస్తున్నాము...'):
        raw_data = get_nse_data(symbol)
        
        if raw_data:
            df_flow = process_option_flow(raw_data)
            
            if not df_flow.empty:
                # 1. Show the 5-Column Table
                st.subheader(f"Option Flow Analysis - {symbol}")
                st.dataframe(df_flow.head(15), use_container_width=True)
                
                # 2. Show AI Analysis in Telugu
                st.divider()
                st.markdown(generate_telugu_analysis(df_flow))
            else:
                st.warning("డేటా ప్రాసెస్ చేయడంలో ఇబ్బంది కలిగింది.")
        else:
            st.error("NSE నుండి డేటా రావడం లేదు. దయచేసి కాసేపు ఆగి మళ్ళీ ప్రయత్నించండి.")

st.info("గమనిక: ఇది కేవలం ఎడ్యుకేషనల్ పర్పస్ కోసం మాత్రమే.")
