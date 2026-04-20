import streamlit as st
import pandas as pd
import time
from NorenRestApiPy.NorenApi import NorenApi

# =============================
# API CLASS
# =============================
class ShoonyaApiPy(NorenApi):
    def __init__(self):
        super().__init__(
            host='https://api.shoonya.com/NorenWSTP/',
            websocket='wss://api.shoonya.com/NorenWSTP/'
        )

# =============================
# CONFIG
# =============================
st.set_page_config(page_title="NSE PRO TERMINAL", layout="wide")
st.title("🚀 Shoonya LIVE OPTION CHAIN PRO")

# =============================
# SESSION STATE
# =============================
if "login" not in st.session_state:
    st.session_state.login = False
if "api" not in st.session_state:
    st.session_state.api = None

# =============================
# SIDEBAR LOGIN
# =============================
with st.sidebar:
    st.header("🔐 Shoonya Login")

    user_id = st.text_input("User ID", value=st.secrets["shoony"]["user_id"])
    password = st.text_input("Password", type="password", value=st.secrets["shoony"]["password"])
    totp = st.text_input("TOTP (6-digit OTP)")

    index = st.selectbox("Select Index", ["NIFTY", "BANKNIFTY"])
    login_btn = st.button("🚀 Login")

# =============================
# LOGIN FUNCTION
# =============================
if login_btn:
    try:
        api = ShoonyaApiPy()
        ret = api.login(
            userid=user_id,
            password=password,
            twoFA=totp,
            vendor_code=st.secrets["shoony"]["vendor_code"],
            api_secret=st.secrets["shoony"]["api_secret"],
            imei=st.secrets["shoony"]["imei"]
        )

        if not ret:
            st.error("❌ Empty response. Check secrets / OTP")
        elif ret.get("stat") == "Ok":
            st.success(f"✅ Welcome {ret.get('uname')}")
            st.session_state.login = True
            st.session_state.api = api
        else:
            st.error(f"❌ Login Failed: {ret.get('emsg')}")
    except Exception as e:
        st.error(f"Error: {e}")

# =============================
# CACHE TOKENS (FAST)
# =============================
@st.cache_data(ttl=3600)
def get_option_tokens(api, index, strikes):
    tokens = []
    for strike in strikes:
        ce_symbol = f"{index} {strike} CE"
        pe_symbol = f"{index} {strike} PE"

        ce = api.search_scrip(exchange="NFO", searchtext=ce_symbol)
        pe = api.search_scrip(exchange="NFO", searchtext=pe_symbol)

        token_ce = ce["values"][0]["token"] if ce and "values" in ce else None
        token_pe = pe["values"][0]["token"] if pe and "values" in pe else None

        tokens.append((strike, token_ce, token_pe))

    return tokens

# =============================
# MAIN DASHBOARD
# =============================
if st.session_state.login:

    api = st.session_state.api

    # =============================
    # GET SPOT PRICE
    # =============================
    token = "26000" if index == "NIFTY" else "26009"
    quote = api.get_quotes(exch="NSE", token=token)

    if not quote:
        st.error("❌ Spot fetch failed")
        st.stop()

    spot = float(quote["lp"])
    st.metric(f"{index} Spot", f"₹{spot}")

    # =============================
    # STRIKE CALCULATION
    # =============================
    step = 50 if index == "NIFTY" else 100
    atm = round(spot / step) * step
    strikes = [atm + i * step for i in range(-5, 6)]

    st.subheader("📊 Option Chain")

    # =============================
    # GET TOKENS (FAST)
    # =============================
    tokens_data = get_option_tokens(api, index, strikes)

    data = []

    # =============================
    # FETCH LTP
    # =============================
    for strike, token_ce, token_pe in tokens_data:
        try:
            ce_ltp = "-"
            pe_ltp = "-"

            if token_ce:
                q = api.get_quotes(exch="NFO", token=token_ce)
                ce_ltp = q["lp"] if q else "-"

            if token_pe:
                q = api.get_quotes(exch="NFO", token=token_pe)
                pe_ltp = q["lp"] if q else "-"

            data.append({
                "Strike": strike,
                "CE LTP": ce_ltp,
                "PE LTP": pe_ltp
            })

        except Exception as e:
            st.warning(f"{strike}: {e}")

    df = pd.DataFrame(data)

    # =============================
    # ATM Highlight
    # =============================
    def highlight_atm(row):
        if row["Strike"] == atm:
            return ['background-color: yellow'] * 3
        return [''] * 3

    st.dataframe(df.style.apply(highlight_atm, axis=1), use_container_width=True)

    # =============================
    # AUTO REFRESH
    # =============================
    st.caption("🔄 Auto Refresh every 10 sec")
    time.sleep(10)
    st.rerun()
