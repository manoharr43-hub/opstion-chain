import streamlit as st
import pandas as pd
import pyotp
import time
from NorenRestApiPy.NorenApi import NorenApi

# ==========================================
# 1. SHOONYA API CONNECTION CLASS
# ==========================================
class ShoonyaApiPy(NorenApi):
    def __init__(self):
        # నేరుగా ఇనిషియలైజ్ చేయడం వల్ల 'login' ఎర్రర్ రాదు
        NorenApi.__init__(self, host='https://api.shoonya.com/NorenWS/', 
                         websocket='wss://api.shoonya.com/NorenWSToken/')

@st.cache_resource
def get_shoonya_instance():
    api = ShoonyaApiPy()
    try:
        # Secrets నుండి డేటా రీడ్ చేయడం
        u = st.secrets["user_id"]
        p = st.secrets["password"]
        vc = st.secrets["vendor_code"]
        key = st.secrets["api_secret"]
        im = st.secrets["imei"]
        t_key = st.secrets["totp_key"]

        # --- TOTP కీని ఏ మార్పులు లేకుండా నేరుగా క్లీన్ చేయడం ---
        clean_key = "".join(t_key.split()).strip().upper()
        
        # TOTP జనరేషన్
        totp_gen = pyotp.TOTP(clean_key)
        current_otp = totp_gen.now()

        # Login ప్రయత్నం
        ret = api.login(userid=u, password=p, twoFA=current_otp, 
                        vendor_code=vc, api_secret=key, imei=im)
        
        if ret and isinstance(ret, dict) and ret.get('stat') == 'Ok':
            return api
        else:
            return f"Error: {ret.get('emsg') if ret else 'No Response'}"
    except Exception as e:
        return f"System Error: {str(e)}"

# ==========================================
# 2. DATA FETCHING LOGIC
# ==========================================
def fetch_option_chain_data(api, index):
    idx_map = {"NIFTY": "Nifty 50", "BANKNIFTY": "Nifty Bank"}
    try:
        # 1. స్పాట్ ప్రైస్
        quote = api.get_quotes('NSE', idx_map[index])
        if not quote or 'lp' not in quote:
            return None, None
        spot_price = float(quote['lp'])
        
        # 2. ఆప్షన్ చైన్ (ATM కి అటు ఇటు 10 స్ట్రైక్స్)
        chain = api.get_option_chain('NFO', index, spot_price, 10)
        if not chain or 'values' not in chain:
            return spot_price, pd.DataFrame()

        rows = []
        for item in chain['values']:
            rows.append({
                "Strike": float(item['stlk']),
                "Type": item['optt'],
                "LTP": float(item.get('lp', 0)),
                "OI": int(item.get('oi', 0)),
                "Vol": int(item.get('v', 0))
            })
        
        df = pd.DataFrame(rows)
        ce = df[df['Type'] == 'CE'][['Strike', 'LTP', 'OI']].rename(columns={'LTP': 'CE_LTP', 'OI': 'CE_OI'})
        pe = df[df['Type'] == 'PE'][['Strike', 'LTP', 'OI']].rename(columns={'LTP': 'PE_LTP', 'OI': 'PE_OI'})
        
        final_df = pd.merge(ce, pe, on="Strike").sort_values("Strike")
        return spot_price, final_df
    except:
        return None, None

# ==========================================
# 3. STREAMLIT UI SETUP
# ==========================================
st.set_page_config(page_title="Shoonya Pro Option Chain", layout="wide")
st.title("📊 Shoonya Pro Option Chain")

res = get_shoonya_instance()

if isinstance(res, str):
    st.error(f"❌ లాగిన్ ఫెయిల్ అయ్యింది: {res}")
    st.info("చిట్కా: మీ Secrets లో TOTP కీని మరోసారి వెరిఫై చేయండి.")
elif res is not None:
    st.success("✅ Shoonya Connected Successfully!")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        symbol = st.selectbox("Select Index", ["NIFTY", "BANKNIFTY"])
    
    spot, df = fetch_option_chain_data(res, symbol)
    
    if spot:
        st.metric(f"{symbol} Spot Price", f"₹{spot}")
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("ఆప్షన్ చైన్ డేటా అందుబాటులో లేదు.")
    
    st.caption("🔄 Auto-refreshing every 15 seconds...")
    time.sleep(15)
    st.rerun()
else:
    st.warning("🔄 లాగిన్ కోసం ప్రయత్నిస్తోంది...")
    
