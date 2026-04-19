import streamlit as st
import requests
import pandas as pd

# =============================
# CONFIG
# =============================
st.set_page_config(page_title="NSE Option Chain", layout="wide")
st.title("📊 NSE Option Chain Live")

# =============================
# FUNCTION TO FETCH DATA
# =============================
@st.cache_data(ttl=60)
def get_option_chain(symbol="NIFTY"):
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br"
    }

    session = requests.Session()
    session.get("https://www.nseindia.com", headers=headers)  # cookie
    
    response = session.get(url, headers=headers)
    data = response.json()
    
    return data

# =============================
# USER INPUT
# =============================
symbol = st.selectbox("Select Index", ["NIFTY", "BANKNIFTY", "FINNIFTY"])

# =============================
# FETCH DATA
# =============================
data = get_option_chain(symbol)

# =============================
# PROCESS DATA
# =============================
records = data['records']['data']

rows = []

for item in records:
    strike = item['strikePrice']
    
    ce = item.get('CE', {})
    pe = item.get('PE', {})
    
    row = {
        "Strike": strike,
        "CE OI": ce.get("openInterest", 0),
        "CE Change OI": ce.get("changeinOpenInterest", 0),
        "CE LTP": ce.get("lastPrice", 0),
        
        "PE OI": pe.get("openInterest", 0),
        "PE Change OI": pe.get("changeinOpenInterest", 0),
        "PE LTP": pe.get("lastPrice", 0),
    }
    
    rows.append(row)

df = pd.DataFrame(rows)

# =============================
# DISPLAY
# =============================
st.subheader(f"{symbol} Option Chain")
st.dataframe(df, use_container_width=True)

# =============================
# ANALYSIS
# =============================
st.subheader("📈 Insights")

max_ce_oi = df.loc[df["CE OI"].idxmax()]
max_pe_oi = df.loc[df["PE OI"].idxmax()]

st.write(f"📊 Max CE OI at Strike: {max_ce_oi['Strike']}")
st.write(f"📊 Max PE OI at Strike: {max_pe_oi['Strike']}")

# =============================
# REFRESH BUTTON
# =============================
if st.button("🔄 Refresh"):
    st.cache_data.clear()
    st.rerun()
