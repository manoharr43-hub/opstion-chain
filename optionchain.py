import streamlit as st
import pandas as pd
import pyotp
from NorenRestApiPy import NorenApi
from streamlit_autorefresh import st_autorefresh

# ==========================================
# 1. API CLASS SETUP
# ==========================================
class ShoonyaApiPy(NorenApi):
    def __init__(self):
        # TypeError rakunda direct ga init chestunnam
        NorenApi.__init__(self, 
            host='https://api.shoonya.com/NorenWS/', 
            websocket='wss://api.shoonya.com/NorenWSToken/'
        )

# ==========================================
# 2. LOGIN FUNCTION (CACHED)
# ==========================================
@st.cache_resource
def login_shoonya():
    try:
        # Secrets nundi data teesukuntundi
        creds = st.secrets["shoonya"]
        otp = pyotp.TOTP(creds["totp_key"]).now()

        api = ShoonyaApiPy()
        ret = api.login(
            userid=creds["user_id"],
            password=creds["password"],
            twoFA=otp,
            vendor_code=creds["vendor_code"],
            api_secret=creds["api_secret"],
            imei=creds["imei"]
        )

        if ret and ret.get("stat") == "Ok":
            return api
        else:
            st.error(f"Login Failed: {ret.get('emsg')}")
            return None
    except Exception as e:
        st.error(f"Login Configuration Error: {e}")
        return None

# ==========================================
# 3. DATA FETCHING FUNCTION
# ==========================================
def fetch_option_chain_data(api, symbol):
    try:
        # Index names setup
        idx_name = "Nifty 50" if symbol == "NIFTY" else "Nifty Bank"
        
        # Spot Price teesukovadam
        quote = api.get_quotes("NSE", idx_name)
        if not quote or 'lp' not in quote:
            return None, pd.DataFrame()
            
        spot = float(quote["lp"])

        # Option Chain data (10 strikes up & down)
        chain = api.get_option_chain("NFO", symbol, spot, 10)
        
        if not chain or 'values' not in chain:
            return spot, pd.DataFrame()

        rows = []
        for item in chain["values"]:
            rows.append({
                "Strike": float(item["stlk"]),
                "Type": item["optt"],
                "LTP": float(item.get("lp", 0)),
                "OI": int(item.get("oi", 0)),
            })

        df
