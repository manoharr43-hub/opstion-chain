import base64
import pyotp
import streamlit as st

def get_shoonya_instance():
    api = ShoonyaApiPy()
    try:
        # 1. Secret నుండి కీని తీసుకోవడం
        raw_key = st.secrets["totp_key"]
        
        # 2. కీని పూర్తిగా క్లీన్ చేయడం (అక్షరాలు, అంకెలు మాత్రమే ఉంచడం)
        # Base32 లో కేవలం A-Z మరియు 2-7 మాత్రమే ఉండాలి
        import re
        clean_key = re.sub(r'[^A-Z2-7]', '', raw_key.upper())
        
        # 3. ఒకవేళ కీ లెంగ్త్ సరిగ్గా లేకపోతే ప్యాడింగ్ ఇవ్వడం
        missing_padding = len(clean_key) % 8
        if missing_padding:
            clean_key += '=' * (8 - missing_padding)
        
        # 4. ఇప్పుడు TOTP జనరేట్ చేయడం
        totp_gen = pyotp.TOTP(clean_key)
        current_otp = totp_gen.now()
        
        # 5. లాగిన్
        ret = api.login(userid=st.secrets["user_id"], 
                        password=st.secrets["password"], 
                        twoFA=current_otp, 
                        vendor_code=st.secrets["vendor_code"], 
                        api_secret=st.secrets["api_secret"], 
                        imei=st.secrets["imei"])
        
        if ret and ret.get('stat') == 'Ok':
            return api
    except Exception as e:
        st.error(f"TOTP/Login Error: {e}")
    return None
