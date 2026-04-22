import streamlit as st
import pandas as pd
import pyotp
import requests
from NorenRestApiPy.NorenApi import NorenApi
from streamlit_autorefresh import st_autorefresh

# ==========================================
# 1. API INITIALIZATION
# ==========================================
def get_api_instance():
    api = NorenApi(host='https://api.shoonya.com/NorenWS/', 
                   websocket='wss://api.shoonya.com/NorenWSToken/')
    return api

# ==========================================
# 2. LOGIN FUNCTION (Enhanced Error Checking)
# ==========================================
@st.cache_resource
def login_shoonya():
    try:
        if "shoonya" not in st.secrets:
            st.error("Secrets.toml లో [shoonya] సెక్షన్ లేదు!")
            return None
            
        creds = st.secrets["shoonya"]
        
        # TOTP Generation
        try:
            otp = pyotp.TOTP(creds["totp_key"].replace(" ", "")).now()
        except Exception as e:
            st.error(f"TOTP Key లో లోపం ఉంది: {e}")
            return None

        api = get_api_instance()
        
        # Login Attempt
        ret = api.login(
            userid=creds["user_id"], 
            password=creds["password"],
            twoFA=otp, 
            vendor_code=creds["vendor_code"],
            api_secret=creds["api_secret"], 
            imei=creds["imei"]
        )
        
        if ret is None:
            st.error("Shoonya సర్వర్ నుండి ఎలాంటి రెస్పాన్స్ రావడం లేదు. దయచేసి కాసేపు ఆగి ప్రయత్నించండి.")
            return None
            
        if ret.get("stat") == "Ok":
            return api
        else:
            st.error(f"లాగిన్ ఫెయిల్ అయ్యింది: {ret.get('emsg')}")
            return None
            
    except Exception as e:
        st.error(f"నెట్‌వర్క్ లేదా సెటప్ ఎర్రర్: {e}")
        return None

# ==========================================
# 3. DATA FETCHING
# ==========================================
def get_option_chain(api, symbol):
    try:
        idx_map = {"NIFTY": "Nifty 50", "BANKNIFTY": "Nifty Bank"}
        quote = api.get_quotes("NSE", idx_map[symbol])
        
        if not quote or 'lp' not in quote:
            return None, pd.DataFrame()
            
        spot = float(quote["lp"])
        chain = api.get_option_chain("NFO", symbol, spot, 10)
        
        if not chain or 'values' not in chain:
            return spot, pd.DataFrame()

        data_list = []
        for i in chain["values"]:
            data_list.append({
                "Strike": float(i["stlk"]),
                "Type": i["optt"],
                "LTP": float(i.get("lp", 0)),
                "OI": int(i.get("oi", 0))
            })
            
        df = pd.DataFrame(data_list)
        ce = df[df["Type"] == "CE"].rename(columns={"LTP": "CE_LTP", "OI": "CE_OI"})
        pe = df[df["Type"] == "PE"].rename(columns={"LTP": "PE_LTP", "OI": "PE_OI"})
        
        final = pd.merge(ce[["Strike", "CE_LTP", "CE_OI"]], 
                         pe[["Strike", "PE_LTP", "PE_OI"]], on="Strike").sort_values("Strike")
        return spot, final
    except:
        return None, pd.DataFrame()

# ==========================================
# 4. STREAMLIT UI
# ==========================================
st.set_page_config(page_title="Shoonya Option Chain", layout="wide")
st.title("📊 Live Option Chain")

# 10 Seconds Refresh
st_autorefresh(interval=10000, key="datarefresh")

api = login_shoonya()

if api:
    st.sidebar.success("✅ Connected")
    symbol = st.selectbox("ఇండెక్స్ ఎంచుకోండి", ["NIFTY", "BANKNIFTY"])
    
    spot, df = get_option_chain(api, symbol)
    
    if spot:
        st.subheader(f"{symbol} Spot: ₹{spot}")
        
    if not df.empty:
        st.dataframe(df.style.format({
            "CE_LTP": "{:.2f}", "PE_LTP": "{:.2f}",
            "Strike": "{:.0f}", "CE_OI": "{:,}", "PE_OI": "{:,}"
        }), use_container_width=True, height=600)
    else:
        st.info("డేటా లోడ్ అవుతోంది... దయచేసి వేచి ఉండండి.")
