import streamlit as st
import requests
import hashlib
import pandas as pd

# =============================
# CONFIG
# =============================
st.set_page_config(page_title="🔥 NSE AI ULTRA PRO", layout="wide")
st.title("🚀 NSE AI ULTRA PRO (Shoonya Direct API)")

# =============================
# LOAD SECRETS
# =============================
try:
    USER_ID = st.secrets["USER_ID"]
    PASSWORD = st.secrets["PASSWORD"]
    API_SECRET = st.secrets["API_SECRET"]
    TOTP = st.secrets["TOTP"]
except:
    st.error("❌ secrets.toml not configured properly")
    st.stop()

# =============================
# LOGIN FUNCTION
# =============================
def login():
    url = "https://api.shoonya.com/NorenWClientTP/QuickAuth"

    payload = {
        "uid": USER_ID,
        "pwd": hashlib.sha256(PASSWORD.encode()).hexdigest(),
        "factor2": TOTP,
        "vc": "FA",
        "appkey": hashlib.sha256(API_SECRET.encode()).hexdigest(),
        "imei": "abc1234"
    }

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    res = requests.post(url, data=payload, headers=headers)

    try:
        data = res.json()
        if data.get("stat") == "Ok":
            st.success("✅ Login Success")
            return data.get("susertoken")
        else:
            st.error(f"❌ Login Failed: {data}")
            return None
    except:
        st.error("❌ API not returning JSON (maybe blocked)")
        st.write(res.text)
        return None


# =============================
# OPTION CHAIN FUNCTION
# =============================
def get_option_chain(token):
    url = "https://api.shoonya.com/NorenWClientTP/GetOptionChain"

    payload = {
        "uid": USER_ID,
        "token": token,
        "exch": "NFO",
        "tsym": "NIFTY",
        "cnt": "10"
    }

    res = requests.post(url, data=payload)

    try:
        data = res.json()
        return data
    except:
        st.error("❌ Option chain fetch failed")
        st.write(res.text)
        return None


# =============================
# MAIN BUTTON
# =============================
if st.button("🔐 Login & Load Data"):

    token = login()

    if not token:
        st.stop()

    option_data = get_option_chain(token)

    if not option_data:
        st.stop()

    call_rows = []
    put_rows = []

    # =============================
    # PARSE DATA
    # =============================
    for row in option_data:

        ce = row.get("CE", {})
        pe = row.get("PE", {})

        if ce:
            call_rows.append({
                "Strike": ce.get("strprc"),
                "OI": int(ce.get("oi", 0)),
                "Chg OI": int(ce.get("oi_chg", 0)),
                "LTP": float(ce.get("lp", 0))
            })

        if pe:
            put_rows.append({
                "Strike": pe.get("strprc"),
                "OI": int(pe.get("oi", 0)),
                "Chg OI": int(pe.get("oi_chg", 0)),
                "LTP": float(pe.get("lp", 0))
            })

    call_df = pd.DataFrame(call_rows)
    put_df = pd.DataFrame(put_rows)

    if call_df.empty or put_df.empty:
        st.warning("⚠️ No data received")
        st.stop()

    # =============================
    # METRICS
    # =============================
    call_oi = call_df["OI"].sum()
    put_oi = put_df["OI"].sum()

    call_chg = call_df["Chg OI"].sum()
    put_chg = put_df["Chg OI"].sum()

    pcr = round(put_oi / call_oi, 2) if call_oi else 1

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("CALL OI", call_oi)
    col2.metric("CALL OI Chg", call_chg)
    col3.metric("PUT OI", put_oi)
    col4.metric("PUT OI Chg", put_chg)
    col5.metric("PCR", pcr)

    # =============================
    # TABLES
    # =============================
    st.subheader("🔥 Top CALL OI")
    st.dataframe(call_df.sort_values("OI", ascending=False).head(5))

    st.subheader("🔥 Top PUT OI")
    st.dataframe(put_df.sort_values("OI", ascending=False).head(5))

    # =============================
    # SIGNAL
    # =============================
    bias = "SIDEWAYS"

    if pcr > 1.2:
        bias = "BULLISH 🚀"
    elif pcr < 0.8:
        bias = "BEARISH 🔻"

    signal = "WAIT"

    if bias == "BULLISH 🚀" and put_chg > call_chg:
        signal = "🔥 CE BUY"
    elif bias == "BEARISH 🔻" and call_chg > put_chg:
        signal = "🔥 PE BUY"

    st.success(f"🤖 AI Signal: {signal}")
