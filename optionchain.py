import streamlit as st
import requests
import pandas as pd

# =============================
# CONFIG
# =============================
st.set_page_config(page_title="NSE Option Chain PRO", layout="wide")
st.title("📊 NSE Option Chain Live (Stable Version)")

# =============================
# SESSION (IMPORTANT FIX)
# =============================
@st.cache_resource
def create_session():
    session = requests.Session()

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com"
    }

    session.headers.update(headers)

    # Get cookies first (VERY IMPORTANT)
    try:
        session.get("https://www.nseindia.com", timeout=5)
    except:
        pass

    return session

session = create_session()

# =============================
# FETCH DATA
# =============================
@st.cache_data(ttl=60)
def get_option_chain(symbol):
    try:
        url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"

        response = session.get(url, timeout=10)

        if response.status_code != 200:
            return None

        return response.json()

    except Exception as e:
        st.error(f"API Error: {e}")
        return None

# =============================
# UI INPUT
# =============================
symbol = st.selectbox("Select Index", ["NIFTY", "BANKNIFTY", "FINNIFTY"])

# =============================
# LOAD BUTTON
# =============================
if st.button("📥 Load Option Chain"):

    with st.spinner("⏳ Fetching live NSE data..."):
        data = get_option_chain(symbol)

    if not data:
        st.warning("⚠️ Data not received. NSE may be blocking request. Try again.")
        st.stop()

    # =============================
    # PROCESS DATA
    # =============================
    records = data.get("records", {}).get("data", [])

    rows = []

    for item in records:
        strike = item.get("strikePrice")

        ce = item.get("CE", {})
        pe = item.get("PE", {})

        rows.append({
            "Strike": strike,

            "CE OI": ce.get("openInterest", 0),
            "CE Change OI": ce.get("changeinOpenInterest", 0),
            "CE LTP": ce.get("lastPrice", 0),

            "PE OI": pe.get("openInterest", 0),
            "PE Change OI": pe.get("changeinOpenInterest", 0),
            "PE LTP": pe.get("lastPrice", 0),
        })

    df = pd.DataFrame(rows)

    # =============================
    # DISPLAY TABLE
    # =============================
    st.subheader(f"{symbol} Option Chain Data")
    st.dataframe(df, use_container_width=True)

    # =============================
    # INSIGHTS
    # =============================
    st.subheader("📈 Market Insights")

    try:
        max_ce = df.loc[df["CE OI"].idxmax()]
        max_pe = df.loc[df["PE OI"].idxmax()]

        st.success(f"📊 Max CE OI Strike: {max_ce['Strike']}")
        st.success(f"📊 Max PE OI Strike: {max_pe['Strike']}")

    except:
        st.warning("Not enough data for insights")

# =============================
# REFRESH INFO
# =============================
st.caption("👉 Click 'Load Option Chain' again to refresh live data")
