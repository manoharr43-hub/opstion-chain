import streamlit as st
import pandas as pd
import requests
import time

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Ultra Pro AI Option Chain", layout="wide")


# =========================
# SAFE NSE DATA FETCH
# =========================
def get_nse_data(symbol="NIFTY"):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com/option-chain"
    }

    session = requests.Session()

    try:
        # warm-up call (important for cookies)
        session.get("https://www.nseindia.com", headers=headers, timeout=10)

        url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"

        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        return response.json()

    except Exception as e:
        st.error(f"❌ NSE Fetch Error: {e}")
        return None


# =========================
# SAFE DATA PROCESSING
# =========================
def process_option_flow(data):
    try:
        if not data:
            return pd.DataFrame()

        records = data.get("filtered", {}).get("data", [])
        if not records:
            return pd.DataFrame()

        flow_list = []

        for entry in records:
            strike = entry.get("strikePrice", 0)

            ce = entry.get("CE", {})
            pe = entry.get("PE", {})

            ce_oi = ce.get("changeinOpenInterest", 0)
            pe_oi = pe.get("changeinOpenInterest", 0)

            oi_diff = pe_oi - ce_oi

            sentiment = "Bullish" if oi_diff > 0 else "Bearish"

            flow_list.append({
                "Strike Price": strike,
                "CE Change OI": ce_oi,
                "PE Change OI": pe_oi,
                "OI Difference": oi_diff,
                "Market Sentiment": sentiment
            })

        return pd.DataFrame(flow_list)

    except Exception as e:
        st.error(f"Processing Error: {e}")
        return pd.DataFrame()


# =========================
# TELUGU AI ANALYSIS
# =========================
def generate_telugu_analysis(df):
    if df is None or df.empty:
        return "⚠️ విశ్లేషణకు డేటా లేదు."

    total_ce = df["CE Change OI"].sum()
    total_pe = df["PE Change OI"].sum()

    if total_pe > total_ce:
        trend = "📈 బుల్లిష్ మార్కెట్ అవకాశం"
        strategy = "PE ఎక్కువ ఉన్న సపోర్ట్ జోన్ గమనించండి"
    else:
        trend = "📉 బేరిష్ మార్కెట్ అవకాశం"
        strategy = "CE ఎక్కువ ఉన్న రెసిస్టెన్స్ జోన్ గమనించండి"

    return f"""
### 📊 AI OPTION CHAIN ANALYSIS (TELUGU)

- **ట్రెండ్:** {trend}
- **CE Total OI:** {total_ce}
- **PE Total OI:** {total_pe}

**ట్రేడ్ ఐడియా:**
{strategy}
"""


# =========================
# UI
# =========================
st.title("🚀 ULTRA PRO AI OPTION CHAIN (STABLE VERSION)")

with st.sidebar:
    st.header("INDEX SELECT")
    symbol = st.selectbox("Choose Index", ["NIFTY", "BANKNIFTY", "FINNIFTY"])
    run = st.button("RUN ANALYSIS")


# =========================
# MAIN LOGIC
# =========================
if run:
    with st.spinner("Fetching NSE data..."):

        data = get_nse_data(symbol)

        if data:

            df = process_option_flow(data)

            if df is not None and not df.empty:

                st.subheader(f"📊 Option Flow - {symbol}")
                st.dataframe(df.head(20), use_container_width=True)

                st.divider()
                st.markdown(generate_telugu_analysis(df))

            else:
                st.warning("⚠️ Data processing failed or empty response")

        else:
            st.error("❌ NSE data not available. Try again later.")


st.info("⚠️ Educational Purpose Only - Not Financial Advice")
