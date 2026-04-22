import streamlit as st
import pandas as pd
import pyotp
from NorenRestApiPy import NorenApi
from streamlit_autorefresh import st_autorefresh

# ==========================================
# API CLASS
# ==========================================
class ShoonyaApiPy(NorenApi):
    def __init__(self):
        super().__init__(
            host='https://api.shoonya.com/NorenWS/',
            websocket='wss://api.shoonya.com/NorenWSToken/'
        )

# ==========================================
# LOGIN (STAY CONNECTED)
# ==========================================
@st.cache_resource
def login_shoonya():
    try:
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
        return None
    except Exception as e:
        st.error(f"Login Error: {e}")
        return None

# ==========================================
# FETCH DATA & PCR
# ==========================================
def fetch_data(api, symbol):
    try:
        idx_map = {"NIFTY": "NSE|Nifty 50", "BANKNIFTY": "NSE|Nifty Bank"}
        quote = api.get_quotes("NSE", idx_map[symbol].split('|')[1])
        spot = float(quote["lp"])

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
        ce = df[df["Type"] == "CE"].rename(columns={"LTP": "CE_LTP", "OI": "CE_OI"})
        pe = df[df["Type"] == "PE"].rename(columns={"LTP": "PE_LTP", "OI": "PE_OI"})
        
        final = pd.merge(ce[["Strike", "CE_LTP", "CE_OI"]], 
                         pe[["Strike", "PE_LTP", "PE_OI"]], on="Strike").sort_values("Strike")
        
        return spot, final
    except Exception as e:
        st.error(f"Data Fetching Error: {e}")
        return None, pd.DataFrame()

# ==========================================
# UI DESIGN
# ==========================================
st.set_page_config(page_title="Shoonya Option Chain", layout="wide")

# Side bar for Refresh settings
with st.sidebar:
    st.header("Settings")
    refresh_int = st.slider("Refresh Interval (Seconds)", 5, 60, 10)
    st_autorefresh(interval=refresh_int * 1000, key="datarefresh")

st.title("📊 Shoonya Option Chain PRO")

api = login_shoonya()

if api:
    col1, col2 = st.columns([1, 3])
    with col1:
        symbol = st.selectbox("Select Index", ["NIFTY", "BANKNIFTY"])
    
    spot, df = fetch_data(api, symbol)

    if spot and not df.empty:
        # PCR Calculation
        total_ce_oi = df["CE_OI"].sum()
        total_pe_oi = df["PE_OI"].sum()
        pcr = round(total_pe_oi / total_ce_oi, 2) if total_ce_oi > 0 else 0

        # Dashboard Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric(f"{symbol} Spot", f"₹{spot}")
        m2.metric("Total PCR", pcr)
        m3.info("Live Data Auto-refreshing...")

        # Highlight ATM (At The Money) Strike
        def highlight_atm(s):
            is_atm = abs(s.Strike - spot) == min(abs(df.Strike - spot))
            return ['background-color: #2c3e50' if is_atm else '' for _ in s]

        st.table(df.style.apply(highlight_atm, axis=1).format({
            "CE_LTP": "{:.2f}", "PE_LTP": "{:.2f}", 
            "Strike": "{:.0f}", "CE_OI": "{:,}", "PE_OI": "{:,}"
        }))
    else:
        st.warning("Data load avvaledu. దయచేసి మార్కెట్ సమయం అయిందో లేదో చూడండి.")
else:
    st.error("Login Failed! Please check your st.secrets.")
