import pyotp
import re
import streamlit as st

def get_shoonya_instance():
    api = ShoonyaApiPy()
    try:
        # 1. Secret నుండి కీని తీసుకోవడం
        raw_key = st.secrets["totp_key"]
        
        # 2. Base32 కి పనికిరాని అక్షరాలన్నింటినీ తొలగించడం
        # కేవలం A-Z మరియు 2-7 మాత్రమే ఉండాలి
        clean_key = re.sub(r'[^A-Z2-7]', '', raw_key.upper())
        
        # 3. TOTP జనరేట్ చేయడం
        totp_gen = pyotp.TOTP(clean_key)
        current_otp = totp_gen.now()
        
        # 4. లాగిన్
        ret = api.login(userid=st.secrets["user_id"], 
                        password=st.secrets["password"], 
                        twoFA=current_otp, 
                        vendor_code=st.secrets["vendor_code"], 
                        api_secret=st.secrets["api_secret"], 
                        imei=st.secrets["imei"])
        
        if ret and ret.get('stat') == 'Ok':
            return api
        else:
            st.error(f"Shoonya Login Failed: {ret.get('emsg')}")
    except Exception as e:
        st.error(f"TOTP Error: {e}")
    return None
    
