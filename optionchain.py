import streamlit as st
import pandas as pd
import requests
import time

# --- Page Configuration ---
st.set_page_config(page_title="NSE Option Chain - AI Analysis", layout="wide")

# --- NSE API Fetching Logic ---
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9'
}

def get_nse_data(symbol="NIFTY"):
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    session = requests.Session()
    try:
        # Initial call to get cookies
        session.get("https://www.nseindia.com", headers=headers, timeout=10)
        response = session.get(url, headers=headers, timeout=10)
        return response.json()
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

# --- Process Data for Option Flow ---
def process_option_flow(data):
    records = data['filtered']['data']
    flow_list = []
    
    for entry in records:
        strike_price = entry['strikePrice']
        if 'CE' in entry and 'PE' in entry:
            ce_oi = entry['CE']['changeinOpenInterest']
            pe_oi = entry['PE']['changeinOpenInterest']
            
            # Difference for Trend Analysis
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

# --- Telugu AI Analysis Generator ---
def generate_telugu_analysis(df):
    total_ce_oi = df["CE Change in OI"].sum()
    total_pe_oi = df["PE Change in OI"].sum()
    
    if total_pe_oi > total_ce_oi:
        trend = "బుల్లిష్ (Bullish) - మార్కెట్ పెరిగే అవకాశం ఉంది."
        strategy = "సపోర్ట్ లెవెల్స్ వద్ద కాల్ ఆప్షన్స్ (CE) పై దృష్టి పెట్టండి."
    else:
        trend = "బేరిష్ (Bearish) - మార్కెట్ తగ్గే అవకాశం ఉంది."
        strategy = "రెసిస్టెన్స్ లెవెల్స్ వద్ద పుట్ ఆప్షన్స్ (PE) పై దృష్టి పెట్టండి."
        
    analysis = f"""
    ### 📊 AI మార్కెట్ విశ్లేషణ (Telugu)
    - **ప్రస్తుత ట్రెండ్:** {trend}
    - **గమనిక:** PE OI ఎక్కువగా ఉంటే మార్కెట్ సపోర్ట్ బలంగా ఉన్నట్లు, CE OI ఎక్కువగా ఉంటే రెసిస్టెన్స్ బలంగా ఉన్నట్లు.
    - **ట్రేడ్ ప్లాన్:** {strategy}
    """
    return analysis

# --- Streamlit UI ---
st.title("📈 Live NSE Option Chain & AI Trade Plan")

symbol = st.selectbox("Select Index", ["NIFTY", "BANKNIFTY", "FINNIFTY"])

if st.button("Refresh Data"):
    raw_data = get_nse_data(symbol)
    
    if raw_data:
        df_flow = process_option_flow(raw_data)
        
        # 1. Show Option Flow Table (5 Columns)
        st.subheader(f"Option Flow Analysis - {symbol}")
        st.table(df_flow.head(10)) # Top 10 rows for clarity
        
        # 2. Show AI Analysis in Telugu
        st.divider()
        telugu_report = generate_telugu_analysis(df_flow)
        st.markdown(telugu_report)
        
    else:
        st.warning("Data అందుబాటులో లేదు. దయచేసి మళ్ళీ ప్రయత్నించండి.")

st.info("గమనిక: ఇది కేవలం ఎడ్యుకేషనల్ పర్పస్ కోసం మాత్రమే. ట్రేడింగ్ చేసే ముందు మీ ఫైనాన్షియల్ అడ్వైజర్‌ని సంప్రదించండి.")
