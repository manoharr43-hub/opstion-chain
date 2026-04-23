import streamlit as st
import pandas as pd
import requests
import pyotp

st.set_page_config(layout="wide")
st.title("🚀 Shoonya Direct API Option Chain")

# =========================
# LOGIN FUNCTION
# =========================
def login():
    creds = st.secrets["shoonya"]

    otp = pyotp.TOTP(creds["totp_key"]).now()

    url = "https://api.shoonya.com/NorenWSTP/QuickAuth"

    payload = {
        "uid": creds["user_id"],
        "pwd": creds["password"],
        "factor2": otp,
        "vc": creds["vendor_code"],
        "appkey": creds["api_secret"],
        "imei": creds["imei"]
    }

    res = requests.post(url, data=payload)
    data = res.json()

    if data.get("stat") == "Ok":
        return data["susertoken"]
    else:
        st.error(data)
        return None


# =========================
# GET SPOT PRICE
# =========================
def get_spot(token):
    user = st.secrets["shoonya"]["user_id"]

    url = "https://api.shoonya.com/NorenWSTP/GetQuotes"

    payload = {
        "uid": user,
        "exch": "NSE",
        "token": "26000",  # NIFTY
        "susertoken": token
    }

    res = requests.post(url, data=payload)
    data = res.json()

    return float(data.get("lp", 0))


# =========================
# FAKE OPTION CHAIN (SAFE)
# =========================
def option_chain(spot):
    base = int(round(spot / 50) * 50)

    strikes = [base + i*50 for i in range(-5, 6)]

    data = []

    for s in strikes:
        data.append({
            "Strike": s,
            "CE_OI": 1000 + s,
            "PE_OI": 1200 + s,
            "CE_LTP": 100,
            "PE_LTP": 120
        })

    return pd.DataFrame(data)


# =========================
# MAIN APP
# =========================
token = login()

if token:
    st.success("✅ Login Successful")

    spot = get_spot(token)
    st.subheader(f"NIFTY Spot: ₹{spot}")

    df = option_chain(spot)

    # PCR
    total_ce = df["CE_OI"].sum()
    total_pe = df["PE_OI"].sum()
    pcr = total_pe / total_ce

    col1, col2, col3 = st.columns(3)
    col1.metric("PCR", round(pcr, 2))
    col2.metric("Total CE OI", total_ce)
    col3.metric("Total PE OI", total_pe)

    # SIGNAL
    if pcr > 1:
        st.success("🟢 BUY SIGNAL")
    else:
        st.error("🔴 SELL SIGNAL")

    st.dataframe(df, use_container_width=True)

else:
    st.error("❌ Login Failed")
