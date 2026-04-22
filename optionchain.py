import streamlit as st
import pandas as pd
import pyotp
from NorenRestApiPy.NorenApi import NorenApi
from streamlit_autorefresh import st_autorefresh

# ==========================================
# 1. API INITIALIZATION
# ==========================================
def get_api_instance():
    # Prism URL try chestunnam, idi ekkuva stable ga untundi
    api = NorenApi(host='https://api.shoonya.com/NorenWS/', 
                   websocket='wss://api.shoonya.com/NorenWSToken/')
    return api

# ==========================================
# 2. LOGIN FUNCTION
# ==========================================
@st.cache_resource
def login_shoonya():
    try:
        creds = st.secrets["shoonya"]
        # TOTP nundi spaces unte teesestundi
        totp_secret = creds["totp_key"].replace(" ", "").strip()
        otp = pyotp.TOTP(totp_secret).now()

        api = get_api_instance()
        
        # API Secret lo extra spaces unte teesestundi
        api_key = creds["api_secret"].strip()

        ret = api.login(
            userid=creds["user_id"].strip(), 
            password=creds["password"].strip(),
            twoFA=otp, 
            vendor_code=creds["vendor_code"].strip(),
            api_secret=api_key, 
            imei=creds["imei"].strip()
        )
        
        if ret and ret.get("stat") == "Ok":
            return api
        else:
            msg = ret.get("emsg") if ret else "No response from server"
            st.error(f"లాగిన్ కాలేదు: {msg}")
            return None
    except Exception as e:
        st.error(f"సెటప్ లో ఏదో లోపం ఉంది: {e}")
        return None

# ==========================================
# 3. UI & DATA
# ==========================================
st.set_page_config(layout="wide")
st.title("📊 Live Option Chain")

api = login_shoonya()

if api:
    st.sidebar.success("✅ Connected")
    st_autorefresh(interval=10000, key="refresh")
    
    symbol = st.selectbox("Index", ["NIFTY", "BANKNIFTY"])
    # ఇక్కడ మీ డేటా ఫెచింగ్ ఫంక్షన్ (గతంలో ఇచ్చినట్లు) కొనసాగించండి...
    st.info(f"{symbol} డేటా కోసం సిద్ధంగా ఉన్నాం. మార్కెట్ ఓపెన్ అయ్యాక చెక్ చేయండి.")
else:
    st.warning("దయచేసి మీ Shoonya API వివరాలు సరిగ్గా ఉన్నాయో లేదో డాష్‌బోర్డ్‌లో చూడండి.")
