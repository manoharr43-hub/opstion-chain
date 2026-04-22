import streamlit as st
import pandas as pd
import pyotp
from NorenRestApiPy import NorenApi
from streamlit_autorefresh import st_autorefresh

# ==========================================
# 1. API CLASS (TypeError రాకుండా మార్చాను)
# ==========================================
class ShoonyaApiPy(NorenApi):
    def __init__(self):
        # super() కి బదులు నేరుగా NorenApi ని పిలుస్తున్నాం
        NorenApi.__init__(self, 
            host='https://api.shoonya.com/NorenWS/', 
            websocket='wss://api.shoonya.com/NorenWSToken/'
        )

# ==========================================
# 2. LOGIN FUNCTION
# ==========================================
@st.cache_resource
def login_shoonya():
    try:
        if "shoonya" not in st.secrets:
            st.error("Secrets.toml file lo [shoonya] section ledu!")
            return None
            
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
        st.error(f"Login Error: {e}")
        return None

# ==========================================
# 3. DATA FETCHING FUNCTION
# ==========================================
def fetch_data(api, symbol):
    try:
        # Index map for Shoonya
        idx_map = {"NIFTY": "Nifty 50", "BANKNIFTY": "Nifty Bank"}
        quote = api.get_quotes("NSE", idx_map[symbol])
        
        if not quote or 'lp' not in quote:
            return None, pd.DataFrame()
            
        spot = float(quote["lp"])
        
        # Option Chain fetching (10 strikes up & down)
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

        df = pd.DataFrame(rows)
        
        # Separating CE and PE
        ce = df[df["Type"] == "CE"].rename(columns={"LTP": "CE_LTP", "OI": "CE_OI"})
        pe = df[df["Type"] == "PE"].rename(columns={"LTP": "PE_LTP", "OI": "PE_OI"})
        
        # Merging into a single row per Strike
        final_df = pd.merge(
            ce[["Strike", "CE_LTP", "CE_OI"]],
            pe[["Strike", "PE_LTP", "PE_OI"]],
            on="Strike"
        ).sort_values("Strike")
        
        return spot, final_df
    except Exception as e:
        st.error(f"Fetch Error: {e}")
        return None, pd.DataFrame()

# ==========================================
# 4. UI MAIN DASHBOARD
# ==========================================
st.set_page_config(page_title="Shoonya Option Chain", layout="wide")

st.title("📊 Shoonya Live Option Chain")

# Auto-refresh prati 10 seconds కి
st_autorefresh(interval=10000, key="chain_refresh")

api = login_shoonya()

if api:
    st.sidebar.success("✅ Connected")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        symbol = st.selectbox("Select Index", ["NIFTY", "BANKNIFTY"])
    
    spot, df = fetch_data(api, symbol)

    if spot:
        st.subheader(f"Current {symbol} Spot: ₹{spot}")

    if not df.empty:
        # Data table displays
        st.dataframe(df.style.format({
            "CE_LTP": "{:.2f}", "PE_LTP": "{:.2f}",
            "Strike": "{:.0f}", "CE_OI": "{:,}", "PE_OI": "{:,}"
        }), use_container_width=True, height=600)
    else:
        st.info("Market data kosam wait chestunnam... Refresh avvaneevvandi.")
else:
    st.error("Login avaledu. Secrets.toml details check cheyandi.")
