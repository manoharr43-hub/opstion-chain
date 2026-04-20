
import streamlit as st
import pyotp
import re
from NorenRestApiPy.NorenApi import NorenApi

class ShoonyaApiPy(NorenApi):
    def __init__(self):
        super().__init__(host='https://api.shoonya.com/NorenWS/', 
                         websocket='wss://api.shoonya.com/NorenWSToken/')

def get_shoonya_instance():
    api = ShoonyaApiPy()
    try:
        # Secrets నుండి డేటా తీసుకోవడం
        u = st.secrets["user_id"]
        p = st.secrets["password"]
        vc = st.secrets["vendor_code"]
        key = st.secrets["api_secret"]
        im = st.secrets["imei"]
        t_key = st.secrets["totp_key"]

        # --- Base32 ఎర్రర్ రాకుండా కీని క్లీన్ చేయడం ---
        # 0 ని O (Orange) గా, 1 ని I (India) గా మారుస్తుంది (Base32 స్టాండర్డ్ ప్రకారం)
        clean_key = t_key.replace('0', 'O').replace('1', 'I')
        # మిగతా తప్పుడు క్యారెక్టర్లను తీసేస్తుంది
        clean_key = re.sub(r'[^A-Z2-7]', '', clean_key.upper())
        
        # TOTP జనరేట్ చేయడం
        totp = pyotp.TOTP(clean_key).now()

        # Login
        ret = api.login(userid=u, password=p, twoFA=totp, 
                        vendor_code=vc, api_secret=key, imei=im)
        
        if ret and ret.get('stat') == 'Ok':
            return api
    except Exception as e:
        st.error(f"Login Failed: {e}")
    return None

# --- UI ---
st.title("📊 Shoonya Pro Option Chain")
api = get_shoonya_instance()

if api:
    st.success("✅ Shoonya Connected!")
    # మీ ఆప్షన్ చైన్ టేబుల్ కోడ్ ఇక్కడ వస్తుంది...
else:
    st.warning("⚠️ లాగిన్ కాలేదు. దయచేసి Secrets చెక్ చేయండి.")
