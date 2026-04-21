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
        NorenApi.__init__(self, host='https://api.shoonya.com/NorenWS/', 
                         websocket='wss://api.shoonya.com/NorenWSToken/')

def get_shoonya_instance():
    api = ShoonyaApiPy()
    try:
        # మీ కొత్త Secrets పేర్లతో డేటా రీడ్ చేయడం
        # ఒకవేళ మీరు ["shoonya"] టేబుల్ వాడితే st.secrets["shoonya"]["key"] అని వాడాలి
        # లేదా నేరుగా ఇలా ట్రై చేద్దాం:
        
        s = st.secrets["shoonya"] if "shoonya" in st.secrets else st.secrets
        
        u = s["shoonyauser_id"].strip()
        p = s["shoonyapassword"].strip()
        vc = s["shoonyavendor_code"].strip()
        apikey = s["shoonyaapi_secret"].strip()
        im = s["shoonyaimei"].strip()
        t_key = s["shoonyatotp_key"].strip()

        # TOTP జనరేషన్ (మనం QR కోడ్ లో చూసిన కీని క్లీన్ గా వాడటం)
        # 37KX47PO73U5R4P52B64MP25OSB6GDER
        clean_key = "".join(t_key.split()).upper()
        totp_gen = pyotp.TOTP(clean_key)
        current_otp = totp_gen.now()

        # Login ప్రయత్నం
        ret = api.login(userid=u, password=p, twoFA=current_otp, 
                        vendor_code=vc, api_secret=apikey, imei=im)
        
        if ret and isinstance(ret, dict) and ret.get('stat') == 'Ok':
            return api
        else:
            msg = ret.get('emsg') if isinstance(ret, dict) else "Server busy"
            return f"Login Failed: {msg}"
    except Exception as e:
        return f"Setup Error: {str(e)}"

# ==========================================
# 2. DATA FETCHING LOGIC
# ==========================================
def fetch_option_chain_data(api, index):
    idx_map = {"NIFTY": "Nifty 50", "BANKNIFTY": "Nifty Bank"}
    try:
        quote = api.get_quotes('NSE', idx_map[index])
        if not quote or 'lp' not in quote:
            return None, None
        spot_price = float(quote['lp'])
        
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
# 3. STREAMLIT UI
# ==========================================
st.set_page_config(page_title="Shoonya Pro Option Chain", layout="wide")
st.title("📊 Shoonya Pro Option Chain")

res = get_shoonya_instance()

if isinstance(res, str):
    st.error(f"❌ {res}")
    st.info("చిట్కా: మీ Secrets లో వేరియబుల్ పేర్లు మరియు TOTP కీని మరోసారి వెరిఫై చేయండి.")
elif res is not None:
    st.success("✅ Shoonya Connected!")
    
    symbol = st.selectbox("ఇండెక్స్ ఎంచుకోండి", ["NIFTY", "BANKNIFTY"])
    spot, df = fetch_option_chain_data(res, symbol)
    
    if spot:
        st.subheader(f"{symbol} Spot: ₹{spot}")
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("డేటా లోడ్ కాలేదు.")
    
    time.sleep(15)
    st.rerun()
