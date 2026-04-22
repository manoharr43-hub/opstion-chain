import streamlit as st
import pandas as pd
import pyotp
from NorenRestApiPy.NorenApi import NorenApi
from streamlit_autorefresh import st_autorefresh

# ==========================================
# 1. API INITIALIZATION
# ==========================================
@st.cache_resource
def login_shoonya():
    try:
        creds = st.secrets["shoonya"]
        # TOTP generation
        otp = pyotp.TOTP(creds["totp_key"].replace(" ", "").strip()).now()

        api = NorenApi(host='https://api.shoonya.com/NorenWS/', 
                       websocket='wss://api.shoonya.com/NorenWSToken/')
        
        # Login
        ret = api.login(
            userid=creds["user_id"].strip(), 
            password=creds["password"].strip(),
            twoFA=otp, 
            vendor_code=creds["vendor_code"].strip(),
            api_secret=creds["api_secret"].strip(), 
            imei=creds["imei"].strip()
        )
        
        if ret and ret.get("stat") == "Ok":
            return api
        else:
            return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None

# ==========================================
# 2. MAIN UI
# ==========================================
st.set_page_config(layout="wide")
st.title("📊 Live Option Chain")

api = login_shoonya()

if api:
    st.success("Connected!")
    st_autorefresh(interval=10000, key="refresh")
    # Ikkada symbol selection pettandi
    st.write("Market data kosam ready ga unnam.")
else:
    st.error("Login Failed! ದయచేసి Python Version 3.11 కి మార్చండి.")
