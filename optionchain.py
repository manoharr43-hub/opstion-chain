import streamlit as st
import pandas as pd
from NorenRestApiPy.NorenApi import NorenApi
import pyotp
import time

# ==========================================
# 1. SHOONYA LOGIN LOGIC
# ==========================================
class ShoonyaApiPy(NorenApi):
    def __init__(self):
        super().__init__(host='https://api.shoonya.com/NorenWS/', 
                         websocket='wss://api.shoonya.com/NorenWSToken/')

@st.cache_resource
def get_shoonya_instance():
    api = ShoonyaApiPy()
    
    # మీ సెట్టింగ్స్ ఇక్కడ ఇవ్వండి
    # భద్రత కోసం వీటిని st.secrets లేదా env ఫైల్ నుండి రీడ్ చేయడం మంచిది
    credentials = {
        'user': 'YOUR_USER_ID',
        'pwd': 'YOUR_PASSWORD',
        'vc': 'YOUR_VENDOR_CODE_VC',
        'apikey': 'YOUR_API_KEY',
        'totp_key': 'YOUR_TOTP_SECRET_KEY' # Google Authenticator లో ఉండే కీ
    }

    # Generate TOTP
    totp = pyotp.TOTP(credentials['totp_key']).now()

    # Login
    ret = api.login(userid=credentials['user'], 
                    password=credentials['pwd'], 
                    twoFA=totp, 
                    vendor_code=credentials['vc'], 
                    api_secret=credentials['apikey'], 
                    imei='DUMMY_IMEI')
    
    if ret and ret.get('stat') == 'Ok':
        return api
    else:
        st.error(f"Login Failed: {ret.get('emsg') if ret else 'Unknown Error'}")
        return None

# ==========================================
# 2. DATA FETCHING LOGIC
# ==========================================
def fetch_option_chain(api, index):
    # Index symbols mappings
    idx_map = {"NIFTY": "Nifty 50", "BANKNIFTY": "Nifty Bank"}
    trading_symbol = index
    
    # Get Spot Price
    quote = api.get_quotes('NSE', idx_map[index])
    if not quote or 'lp' not in quote:
        return None, None
    
    spot_price = float(quote['lp'])
    
    # Fetch Option Chain from Shoonya
    # stlk_count=10 అంటే ATM కి అటు ఇటు 10 స్ట్రైక్స్ వస్తాయి
    chain = api.get_option_chain('NFO', trading_symbol, spot_price, stlk_count=10)
    
    if not chain or 'values' not in chain:
        return spot_price, pd.DataFrame()

    data = []
    for item in chain['values']:
        data.append({
            "Strike": float(item['stlk']),
            "Type": item['optt'], # CE or PE
            "LTP": float(item['lp']),
            "OI": int(item.get('oi', 0)),
            "Volume": int(item.get('v', 0))
        })
    
    df = pd.DataFrame(data)
    
    # Pivot table to show CE and PE side-by-side
    ce_df = df[df['Type'] == 'CE'][['Strike', 'LTP', 'OI']].rename(columns={'LTP': 'CE_LTP', 'OI': 'CE_OI'})
    pe_df = df[df['Type'] == 'PE'][['Strike', 'LTP', 'OI']].rename(columns={'LTP': 'PE_LTP', 'OI': 'PE_OI'})
    
    final_df = pd.merge(ce_df, pe_df, on="Strike").sort_values("Strike")
    return spot_price, final_df

# ==========================================
# 3. STREAMLIT UI
# ==========================================
st.set_page_config(page_title="Shoonya Option Chain", layout="wide")
st.title("🚀 Shoonya Pro Option Chain")

api = get_shoonya_instance()

if api:
    col1, col2 = st.columns([1, 4])
    with col1:
        symbol = st.selectbox("Select Index", ["NIFTY", "BANKNIFTY"])
        refresh_rate = st.slider("Refresh (seconds)", 5, 60, 15)

    spot, df = fetch_option_chain(api, symbol)

    if spot:
        st.metric(f"{symbol} Spot Price", f"₹{spot}")
        
        if not df.empty:
            # Highlight ATM Row
            st.dataframe(df.style.highlight_min(axis=0, subset=['Strike']), use_container_width=True)
        else:
            st.warning("No option chain data found.")
    
    # Auto-refresh
    time.sleep(refresh_rate)
    st.rerun()
