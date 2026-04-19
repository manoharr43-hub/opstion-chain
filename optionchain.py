import streamlit as st
import pandas as pd
import requests

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(page_title="NSE AI ULTRA PRO (Shoonya Direct API)", layout="wide")
st.title("🚀 NSE AI ULTRA PRO (Shoonya Direct API)")

# ==============================
# LOAD SECRETS
# ==============================
try:
    user_id = st.secrets["shoonyasecrets"]["user_id"]
    password = st.secrets["shoonyasecrets"]["password"]
    api_secret = st.secrets["shoonyasecrets"]["api_secret"]
    totp = st.secrets["shoonyasecrets"]["totp"]
except Exception as e:
    st.error("❌ secrets.toml not configured properly")
    st.stop()

# ==============================
# LOGIN FUNCTION
# ==============================
def shoonyalogin():
    url = "https://api.shoonya.com/NSE/login"
    payload = {
        "user_id": user_id,
        "password": password,
        "api_secret": api_secret,
        "totp": totp
    }
    try:
        res = requests.post(url, json=payload)
        if res.status_code == 200:
            return res.json().get("token")
        else:
            st.error(f"Login failed: {res.text}")
            return None
    except Exception as e:
        st.error(f"Login error: {e}")
        return None

# ==============================
# OPTION CHAIN FETCH
# ==============================
def get_option_chain(symbol, token):
    url = f"https://api.shoonya.com/NSE/optionchain/{symbol}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            return pd.DataFrame(res.json()["data"])
        else:
            st.error(f"Option Chain fetch failed: {res.text}")
            return None
    except Exception as e:
        st.error(f"Error fetching option chain: {e}")
        return None

# ==============================
# MAIN APP
# ==============================
st.sidebar.header("⚙️ Settings")
symbol = st.sidebar.text_input("Enter NSE Symbol", value="NIFTY")

if st.sidebar.button("🔑 Login & Fetch"):
    token = shoonyalogin()
    if token:
        st.success("✅ Login Successful")
        df = get_option_chain(symbol, token)
        if df is not None:
            st.dataframe(df)
            st.download_button("⬇️ Download CSV", df.to_csv(index=False), "option_chain.csv", "text/csv")
    else:
        st.error("❌ Could not login. Check secrets.toml")
