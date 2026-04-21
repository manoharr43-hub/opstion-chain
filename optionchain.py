import streamlit as st
import pandas as pd
import pyotp
import time
from NorenRestApiPy.NorenApi import NorenApi

# API క్లాస్ సెటప్
class ShoonyaApiPy(NorenApi):
    def __init__(self):
        NorenApi.__init__(self, host='https://api.shoonya.com/NorenWS/', 
                         websocket='wss://api.shoonya.com/NorenWSToken/')

def get_shoonya_instance():
    api = ShoonyaApiPy()
    try:
        # Secrets నుండి డేటా తీసుకోవడం (Prefixes ఉన్నా లేకపోయినా పనిచేస్తుంది)
        s = st.secrets
        u = (s.get("user_id") or s.get("shoonyauser_id") or s.get("shoonya", {}).get("shoonyauser_id")).strip()
        p = (s.get("password") or s.get("shoonyapassword") or s.get("shoonya", {}).get("shoonyapassword")).strip()
        vc = (s.get("vendor_code") or s.get("shoonyavendor_code") or s.get("shoonya", {}).get("shoonyavendor_code")).strip()
        apikey = (s.get("api_secret") or s.get("shoonyaapi_secret") or s.get("shoonya", {}).get("shoonyaapi_secret")).strip()
        im = (s.get("imei") or s.get("shoonyaimei") or s.get("shoonya", {}).get("shoonyaimei")).strip()
        t_key = (s.get("totp_key") or s.get("shoonyatotp_key") or s.get("shoonya", {}).get("shoonyatotp_key")).strip()

        # TOTP జనరేషన్
        clean_key = "".join(t_key.split()).upper()
        totp = pyotp.TOTP(clean_key).now()

        # Login ప్రయత్నం
        ret = api.login(userid=u, password=p, twoFA=totp, 
                        vendor_code=vc, api_secret=apikey, imei=im)
        
        if ret and isinstance(ret, dict) and ret.get('stat') == 'Ok':
            return api
        else:
            msg = ret.get('emsg') if isinstance(ret, dict) else "Server Busy (No Response)"
            return f"Login Failed: {msg}"
    except Exception as e:
        return f"Setup Error: {str(e)}"

def fetch_data(api, symbol):
    try:
        idx_name = "Nifty 50" if symbol == "NIFTY" else "Nifty Bank"
        quote = api.get_quotes('NSE', idx_name)
        if quote and 'lp' in quote:
            spot = float(quote['lp'])
            chain = api.get_option_chain('NFO', symbol, spot, 10)
            if chain and 'values' in chain:
                df = pd.DataFrame(chain['values'])
                return spot, df
        return None, None
    except:
        return None, None

# --- UI ---
st.set_page_config(page_title="Shoonya Pro Option Chain", layout="wide")
st.title("📊 Shoonya Pro Option Chain")

res = get_shoonya_instance()

if isinstance(res, str):
    st.error(f"❌ {res}")
    st.info("చిట్కా: మీ Secrets లో వివరాలు మరియు TOTP కీని మరోసారి వెరిఫై చేయండి.")
elif res:
    st.success("✅ Shoonya Connected!")
    sym = st.selectbox("Select Index", ["NIFTY", "BANKNIFTY"])
    spot, df = fetch_data(res, sym)
    if spot:
        st.subheader(f"{sym} Spot: ₹{spot}")
        if not df.empty:
            st.dataframe(df, use_container_width=True)
    
    time.sleep(15)
    st.rerun()
    
