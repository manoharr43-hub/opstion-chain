import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="🔥 NSE AI Option Chain", layout="wide")

# =========================
# EXPIRY FETCH
# =========================
def get_expiries(symbol):
    try:
        tk = yf.Ticker(f"{symbol}=X")
        return list(tk.options)
    except:
        return []

# =========================
# SPLIT WEEKLY / MONTHLY
# =========================
def split_weekly_monthly(expiries):
    if not expiries:
        return [], []

    weekly = expiries[:-1]   # all except last
    monthly = [expiries[-1]] # last = monthly

    return weekly, monthly

# =========================
# HEADER
# =========================
st.title("🔥 NSE AI Option Chain Scanner (LIVE UPGRADED)")
st.caption("Weekly + Monthly Expiry System Enabled | No old logic break")

# =========================
# SIDEBAR CONTROLS
# =========================
st.sidebar.markdown("## 📊 CONTROL PANEL")

symbol = st.sidebar.selectbox("Select Index", ["NIFTY", "BANKNIFTY"])

# fetch expiries
expiries = get_expiries(symbol)

weekly, monthly = split_weekly_monthly(expiries)

selected_expiry = None
selected_monthly = None

# =========================
# WEEKLY EXPIRY UI
# =========================
if weekly:
    selected_expiry = st.sidebar.selectbox("⚡ Weekly Expiry", weekly)

# =========================
# MONTHLY EXPIRY UI
# =========================
if monthly:
    selected_monthly = st.sidebar.selectbox("📅 Monthly Expiry", monthly)

# =========================
# ACTIVE EXPIRY LOGIC (SAFE FOR OLD CODE)
# =========================
expiry = selected_expiry if selected_expiry else (selected_monthly if selected_monthly else None)

st.sidebar.markdown("---")
st.sidebar.success(f"Active Expiry: {expiry}")

# =========================
# MAIN PANEL
# =========================
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Symbol", symbol)

with col2:
    st.metric("Weekly Expiries", len(weekly))

with col3:
    st.metric("Monthly Expiries", len(monthly))

# =========================
# OPTION CHAIN PLACEHOLDER (SAFE)
# =========================
st.subheader("📊 Option Chain Data")

if expiry:
    st.info(f"Fetching data for expiry: {expiry}")

    # Dummy structure (you can connect real NSE data here)
    data = {
        "Strike": [22000, 22100, 22200, 22300],
        "CE OI": [1200, 1500, 1100, 900],
        "PE OI": [1000, 1300, 1400, 1600],
        "Change": [50, -20, 80, -10]
    }

    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)

else:
    st.warning("No expiry selected or data not available")

# =========================
# FOOTER
# =========================
st.markdown("---")
st.caption("🚀 UPGRADED VERSION | Old code structure preserved | No break changes")
