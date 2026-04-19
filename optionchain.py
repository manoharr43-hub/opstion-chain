import streamlit as st
import requests
import pandas as pd
import time

# =============================
# 1. PAGE CONFIG
# =============================
st.set_page_config(page_title="NSE Option Chain PRO", layout="wide")
st.title("📊 NSE Option Chain Live (Stable Pro)")

# =============================
# 2. SESSION MANAGEMENT
# =============================
@st.cache_resource
def get_nse_session():
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
    }
    session.headers.update(headers)
    try:
        # NSE హోమ్ పేజీ విజిట్ చేసి కుకీలు సేకరించడం
        session.get("https://www.nseindia.com", timeout=10)
    except:
        pass
    return session

# =============================
# 3. FETCH DATA FUNCTION
# =============================
@st.cache_data(ttl=60)
def fetch_option_chain(symbol):
    session = get_nse_session()
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    
    for _ in range(3):  # 3 సార్లు ప్రయత్నిస్తుంది
        try:
            response = session.get(url, timeout=15)
            if response.status_code == 200:
                return response.json()
            time.sleep(1)
        except:
            continue
    return None

# =============================
# 4. SIDEBAR SETTINGS
# =============================
st.sidebar.header("Control Panel")
symbol = st.sidebar.selectbox("Select Index", ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"])
load_btn = st.sidebar.button("📥 Load Option Chain")

# =============================
# 5. MAIN LOGIC
# =============================
if load_btn:
    with st.spinner(f"Fetching {symbol} data..."):
        data = fetch_option_chain(symbol)
    
    if data:
        # Get Expiry Dates
        expiries = data.get('records', {}).get('expiryDates', [])
        selected_expiry = st.sidebar.selectbox("Select Expiry", expiries)
        
        # Filter Data for Selected Expiry
        raw_data = data.get('records', {}).get('data', [])
        filtered_data = [row for row in raw_data if row.get('expiryDate') == selected_expiry]
        
        rows = []
        for item in filtered_data:
            strike = item.get('strikePrice')
            ce = item.get('CE', {})
            pe = item.get('PE', {})
            
            rows.append({
                "Strike": strike,
                "CE OI": ce.get('openInterest', 0),
                "CE Chng OI": ce.get('changeinOpenInterest', 0),
                "CE LTP": ce.get('lastPrice', 0),
                "PE LTP": pe.get('lastPrice', 0),
                "PE Chng OI": pe.get('changeinOpenInterest', 0),
                "PE OI": pe.get('openInterest', 0),
            })
        
        df = pd.DataFrame(rows)

        if not df.empty:
            # --- Metrics ---
            total_ce_oi = df['CE OI'].sum()
            total_pe_oi = df['PE OI'].sum()
            pcr = round(total_pe_oi / total_ce_oi, 2) if total_ce_oi > 0 else 0
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Total CE OI", f"{total_ce_oi:,}")
            m2.metric("Total PE OI", f"{total_pe_oi:,}")
            m3.metric("Market PCR", pcr, delta="Bullish" if pcr > 1 else "Bearish")

            # --- Data Table ---
            st.subheader(f"{symbol} Data for {selected_expiry}")
            
            # Highlight Strikes near ATM (వినోదం కోసం కలర్ గ్రేడియంట్)
            styled_df = df.style.background_gradient(subset=['CE OI', 'PE OI'], cmap='Greens')
            st.dataframe(styled_df, use_container_width=True, height=500)
            
            # --- Support & Resistance ---
            st.divider()
            col_s, col_r = st.columns(2)
            try:
                max_ce_strike = df.loc[df['CE OI'].idxmax(), 'Strike']
                max_pe_strike = df.loc[df['PE OI'].idxmax(), 'Strike']
                col_r.error(f"🚀 Resistance (Max CE OI): {max_ce_strike}")
                col_s.success(f"⚓ Support (Max PE OI): {max_pe_strike}")
            except:
                pass
        else:
            st.warning("No data found for the selected expiry.")
    else:
        st.error("NSE సర్వర్ నుండి డేటా రావడం లేదు. కాసేపు ఆగి మళ్ళీ ప్రయత్నించండి (లేదా లోకల్ కంప్యూటర్ లో రన్ చేయండి).")
else:
    st.info("పైన ఉన్న 'Load Option Chain' బటన్ నొక్కి డేటాను చూడండి.")

st.caption("Note: NSE API data is updated every 3-5 minutes.")
