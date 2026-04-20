import streamlit as st
import pandas as pd
from NorenRestApiPy.NorenApi import NorenApi

class ShoonyaApiPy(NorenApi):
    def __init__(self):
        NorenApi.__init__(self, host='https://api.shoonya.com/NorenWSTP/', 
                         websocket='wss://api.shoonya.com/NorenWSTP/')

st.set_page_config(page_title="NSE PRO TERMINAL", layout="wide")
st.title("📊 Shoonya Live Option Chain - PRO")

with st.sidebar:
    st.header("Shoonya Login")
    # మీ వివరాలు ఇక్కడ ఫిక్స్ చేశాను
    u_id   = st.text_input("User ID", value="FA189165")
    u_pwd  = st.text_input("Password", type="password")
    u_totp = st.text_input("TOTP (6 Digits)")
    u_vc   = st.text_input("Vendor Code", value="FA189165_U")
    u_key  = st.text_input("API Key (Secret Code)")
    u_imei = st.text_input("IMEI (IP Address)", value="106.222.234.124")
    
    st.divider()
    target_idx = st.selectbox("Select Index", ["NIFTY", "BANKNIFTY"])
    login_btn = st.button("🚀 Login & Load Dashboard")

if login_btn:
    try:
        api = ShoonyaApiPy()
        # API Secret లో ఏవైనా ఖాళీలు ఉంటే తీసేస్తుంది (strip)
        res = api.login(userid=u_id, password=u_pwd, twoFA=u_totp, 
                       vendor_code=u_vc, api_secret=u_key.strip(), imei=u_imei.strip())
        
        if res and res.get('stat') == 'Ok':
            st.success(f"Success! Connected: {res.get('fname')}")
            # ... (మిగిలిన ఆప్షన్ చైన్ కోడ్)
        else:
            st.error(f"Login Failed: {res.get('emsg') if res else 'Check Details'}")
    except Exception as e:
        st.error(f"Error: {str(e)}")
