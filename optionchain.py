import streamlit as st
import pandas as pd
import pyotp
from NorenRestApiPy.NorenApi import NorenApi
from streamlit_autorefresh import st_autorefresh

# ==========================================
# 1. API INITIALIZATION
# ==========================================
def get_api_instance():
    # Direct ga NorenApi class instance ni create chestunnam
    api = NorenApi(host='https://api.shoonya.com/NorenWS/', 
                   websocket='wss://api.shoonya.com/NorenWSToken/')
    return api

# ==========================================
# 2. LOGIN FUNCTION
# ==========================================
@st.cache_resource
def login_shoonya():
    try:
        if "shoonya" not in st.secrets:
            st.error("Secrets.toml lo [shoonya] section ledu!")
            return None
            
        creds = st.secrets["shoonya"]
        otp = pyotp.TOTP(creds["totp_key"]).now()
        
        api = get_api_instance()
        
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
        st.error(f"Login Error: {e}")
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
    except Exception as e:
        return None, pd.DataFrame()

# ==========================================
# 4. STREAMLIT UI
# ==========================================
st.set_page_config(page_title="Shoonya Option Chain", layout="wide")
st.title("📊 Live Option Chain")

# 10 seconds Auto Refresh
st_autorefresh(interval=10000, key="datarefresh")

api = login_shoonya()

if api:
    st.sidebar.success("✅ Connected to Shoonya")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        symbol = st.selectbox("Select Index", ["NIFTY", "BANKNIFTY"])
    
    spot, df = get_option_chain(api, symbol)
    
    if spot:
        st.subheader(f"{symbol} Spot Price: ₹{spot}")
        
    if not df.empty:
        # Table format lo data chupinchadam
        st.dataframe(df.style.format({
            "CE_LTP": "{:.2f}", "PE_LTP": "{:.2f}",
            "Strike": "{:.0f}", "CE_OI": "{:,}", "PE_OI": "{:,}"
        }), use_container_width=True, height=600)
    else:
        st.info("Market data kosam wait chestunnam... Refresh avvaneevvandi.")
else:
    st.error("Login Failed! Secrets correctly enter chesaro ledo chuskoindi.")
