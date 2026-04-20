import streamlit as st
import pandas as pd
import time
from NorenApi import NorenApi

# =============================
# API CLASS
# =============================
class ShoonyaApiPy(NorenApi):
    def __init__(self):
        super().__init__(
            host='https://api.shoonya.com/NorenWClientTP/',   # ✅ correct
            websocket='wss://api.shoonya.com/NorenWSTP/'
        )

# =============================
# CONFIG
# =============================
st.set_page_config(page_title="Shoonya Option Chain PRO", layout="wide")
st.title("🚀 Shoonya LIVE OPTION CHAIN")

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
    st.header("🔐 Login")

    user_id = st.text_input("User ID", value=st.secrets["shoony"]["user_id"])
    password = st.text_input("Password", type="password", value=st.secrets["shoony"]["password"])
    totp = st.text_input("TOTP (6-digit OTP)")

    index = st.selectbox("Select Index", ["NIFTY", "BANKNIFTY"])
    login_btn = st.button("Login")

# =============================
# LOGIN
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

        st.write("🔍 Login Response:", ret)   # ✅ DEBUG

        if ret and ret.get("stat") == "Ok":
            st.success(f"✅ Welcome {ret.get('uname')}")
            st.session_state.login = True
            st.session_state.api = api
        else:
            st.error(f"❌ Login Failed")

    except Exception as e:
        st.error(f"Error: {e}")

# =============================
# CACHE TOKENS
# =============================
@st.cache_data(ttl=3600)
def get_tokens(api, index, strikes):
    result = []
    for strike in strikes:
        try:
            ce = api.search_scrip("NFO", f"{index} {strike} CE")
            pe = api.search_scrip("NFO", f"{index} {strike} PE")

            token_ce = ce["values"][0]["token"] if ce and "values" in ce else None
            token_pe = pe["values"][0]["token"] if pe and "values" in pe else None

            result.append((strike, token_ce, token_pe))
        except:
            result.append((strike, None, None))

    return result

# =============================
# MAIN DASHBOARD
# =============================
if st.session_state.login:

    api = st.session_state.api

    try:
        # =============================
        # GET SPOT
        # =============================
        token = "26000" if index == "NIFTY" else "26009"
        quote = api.get_quotes("NSE", token)

        if not quote:
            st.error("❌ Spot fetch failed")
            st.stop()

        spot = float(quote["lp"])
        st.metric(f"{index} Spot", f"₹{spot}")

        # =============================
        # STRIKES
        # =============================
        step = 50 if index == "NIFTY" else 100
        atm = round(spot / step) * step
        strikes = [atm + i * step for i in range(-5, 6)]

        st.subheader("📊 Option Chain")

        tokens = get_tokens(api, index, strikes)

        rows = []

        # =============================
        # FETCH DATA
        # =============================
        for strike, tce, tpe in tokens:

            ce_ltp = "-"
            pe_ltp = "-"

            try:
                if tce:
                    q = api.get_quotes("NFO", tce)
                    ce_ltp = q["lp"] if q else "-"

                if tpe:
                    q = api.get_quotes("NFO", tpe)
                    pe_ltp = q["lp"] if q else "-"
            except:
                pass

            rows.append({
                "Strike": strike,
                "CE LTP": ce_ltp,
                "PE LTP": pe_ltp
            })

        df = pd.DataFrame(rows)

        # =============================
        # ATM HIGHLIGHT
        # =============================
        def highlight(row):
            if row["Strike"] == atm:
                return ['background-color: yellow'] * 3
            return [''] * 3

        st.dataframe(df.style.apply(highlight, axis=1), use_container_width=True)

        # =============================
        # AUTO REFRESH
        # =============================
        st.caption("🔄 Auto refresh every 10 sec")
        time.sleep(10)
        st.rerun()

    except Exception as e:
        st.error(f"Runtime Error: {e}")
