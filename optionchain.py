import streamlit as st
import pandas as pd
import requests
from streamlit_autorefresh import st_autorefresh

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="ULTRA NSE AI PRO", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { font-size: 24px; color: #00ffcc; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔥 ULTRA NSE AI OPTION CHAIN (STABLE 3.0)")

# Auto-refresh every 60 seconds to avoid IP Ban
st_autorefresh(interval=60000, key="nse_refresh")

# =========================
# DATA FETCHING ENGINE
# =========================
def fetch_nse_data(symbol):
    """Bypasses NSE blocking by simulating a browser session."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/121.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.nseindia.com/option-chain"
    }
    
    indices = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"]
    if symbol.upper() in indices:
        url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol.upper()}"
    else:
        url = f"https://www.nseindia.com/api/option-chain-equities?symbol={symbol.upper()}"

    try:
        session = requests.Session()
        # Initial call to get cookies
        session.get("https://www.nseindia.com", headers=headers, timeout=10)
        # Actual API call
        response = session.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        st.error(f"NSE Fetch Error: {e}")
        return None

# =========================
# AI ANALYSIS ENGINE
# =========================
def analyze_data(json_data):
    if not json_data or 'records' not in json_data:
        return pd.DataFrame()

    raw_records = json_data['records']['data']
    rows = []

    for item in raw_records:
        strike = item.get('strikePrice')
        ce = item.get('CE', {})
        pe = item.get('PE', {})
        
        rows.append({
            "Strike": strike,
            "CE_OI": ce.get('openInterest', 0),
            "CE_CHG": ce.get('changeinOpenInterest', 0),
            "CE_LTP": ce.get('lastPrice', 0),
            "PE_LTP": pe.get('lastPrice', 0),
            "PE_CHG": pe.get('changeinOpenInterest', 0),
            "PE_OI": pe.get('openInterest', 0),
        })

    df = pd.DataFrame(rows)

    # VECTORIZED LOGIC (Fixes the Truth Value Ambiguity Error)
    df['OI_Diff'] = df['PE_CHG'] - df['CE_CHG']
    
    # Generate Signals
    df['SIGNAL'] = "NEUTRAL"
    # Buy CE if Put Writing (PE_CHG) is 1.8x more than Call Writing
    df.loc[df['PE_CHG'] > df['CE_CHG'] * 1.8, 'SIGNAL'] = "🟢 BUY CE"
    # Buy PE if Call Writing (CE_CHG) is 1.8x more than Put Writing
    df.loc[df['CE_CHG'] > df['PE_CHG'] * 1.8, 'SIGNAL'] = "🔴 BUY PE"

    return df

# =========================
# UI LAYOUT
# =========================
symbol = st.sidebar.selectbox("Market Symbol", ["NIFTY", "BANKNIFTY", "FINNIFTY", "RELIANCE", "SBIN"])

if st.button("🚀 ANALYZE LIVE MARKET"):
    with st.spinner(f"Fetching Live Data for {symbol}..."):
        data = fetch_nse_data(symbol)
        df = analyze_data(data)

    if not df.empty:
        # Metrics Calculation
        total_ce_oi = df['CE_OI'].sum()
        total_pe_oi = df['PE_OI'].sum()
        pcr = total_pe_oi / total_ce_oi if total_ce_oi != 0 else 0
