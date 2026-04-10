import streamlit as st
import pandas as pd
import requests
import time
from streamlit_autorefresh import st_autorefresh

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="NSE AI OPTION CHAIN PRO", layout="wide")
st.title("🔥 NSE AI OPTION CHAIN PRO (NO BLOCK VERSION)")

# auto refresh safe
st_autorefresh(interval=60000, key="refresh")

# =========================
# NSE FETCH (ROBUST VERSION)
# =========================
def fetch_nse(symbol):
    try:
        session = requests.Session()

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.nseindia.com/option-chain",
            "Connection": "keep-alive",
        }

        session.headers.update(headers)

        # warm up cookies
        session.get("https://www.nseindia.com", timeout=10)
        time.sleep(1)

        indices = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"]

        if symbol.upper() in indices:
            url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol.upper()}"
        else:
            url = f"https://www.nseindia.com/api/option-chain-equities?symbol={symbol.upper()}"

        for _ in range(4):
            res = session.get(url, timeout=10)

            if res.status_code == 200:
                return res.json()

            elif res.status_code in [401, 403]:
                time.sleep(2)
                session.get("https://www.nseindia.com", timeout=10)
                continue

        return None

    except Exception as e:
        st.error(f"Fetch Error: {e}")
        return None


# =========================
# PROCESS DATA
# =========================
def process_data(data):
    if not data:
        return pd.DataFrame()

    records = data.get("records", {}).get("data", [])
    rows = []

    for r in records:
        ce = r.get("CE", {})
        pe = r.get("PE", {})

        rows.append({
            "Strike": r.get("strikePrice"),
            "Expiry": r.get("expiryDate"),
            "CE_OI": ce.get("openInterest", 0),
            "CE_CHG_OI": ce.get("changeinOpenInterest", 0),
            "CE_LTP": ce.get("lastPrice", 0),
            "PE_OI": pe.get("openInterest", 0),
            "PE_CHG_OI": pe.get("changeinOpenInterest", 0),
            "PE_LTP": pe.get("lastPrice", 0),
        })

    return pd.DataFrame(rows)


# =========================
# AI SIGNAL ENGINE
# =========================
def ai_signals(df):
    if df.empty:
        return df

    def signal(row):
        if row["PE_CHG_OI"] > row["CE_CHG_OI"] * 1.7:
            return "🚀 BUY (BULLISH)"
        elif row["CE_CHG_OI"] > row["PE_CHG_OI"] * 1.7:
            return "📉 SELL (BEARISH)"
        else:
            return "⚖️ NEUTRAL"

    df["SIGNAL"] = df.apply(signal, axis=1)
    df["OI_DIFF"] = df["PE_CHG_OI"] - df["CE_CHG_OI"]
    return df


# =========================
# UI
# =========================
symbol = st.sidebar.selectbox(
    "Select Index / Stock",
    ["NIFTY", "BANKNIFTY", "FINNIFTY", "RELIANCE", "SBIN", "TCS"]
)

if st.button("🔥 GET AI SIGNALS"):
    with st.spinner("Fetching NSE Data..."):

        data = fetch_nse(symbol)
        df = process_data(data)

        if not df.empty:

            df = ai_signals(df)

            # =========================
            # METRICS
            # =========================
            ce_total = df["CE_OI"].sum()
            pe_total = df["PE_OI"].sum()
            pcr = pe_total / ce_total if ce_total else 0

            col1, col2, col3 = st.columns(3)
            col1.metric("CE OI", f"{ce_total:,}")
            col2.metric("PE OI", f"{pe_total:,}")
            col3.metric("PCR", round(pcr, 2))

            # market sentiment
            if pcr > 1.2:
                st.success("🔥 STRONG BULLISH MARKET")
            elif pcr < 0.8:
                st.error("📉 STRONG BEARISH MARKET")
            else:
                st.warning("⚖️ SIDEWAYS MARKET")

            # =========================
            # SIGNAL TABLE
            # =========================
            st.subheader("🔥 AI SIGNALS")
            st.dataframe(
                df[df["SIGNAL"] != "⚖️ NEUTRAL"]
                .sort_values("OI_DIFF", ascending=False)
                .head(15)
            )

            # =========================
            # FULL DATA
            # =========================
            st.subheader("📊 FULL OPTION CHAIN")
            st.dataframe(df)

        else:
            st.error("❌ Data not loaded. NSE blocked or market closed.")

st.markdown("---")
st.caption("⚠️ Educational tool only. Not financial advice.")
