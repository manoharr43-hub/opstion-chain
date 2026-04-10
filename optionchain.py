import streamlit as st
import pandas as pd
import requests
import time
from streamlit_autorefresh import st_autorefresh

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="ULTRA NSE AI OPTION CHAIN", layout="wide")
st.title("🔥 ULTRA NSE AI OPTION CHAIN (STABLE 2.0)")

# Auto refresh (safe - 60 sec)
st_autorefresh(interval=60000, key="refresh")

# =========================
# NSE FETCH (FIXED + STABLE)
# =========================
def fetch_nse(symbol):
    try:
        session = requests.Session()

        base_url = "https://www.nseindia.com"

        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Referer": "https://www.nseindia.com/option-chain",
            "cache-control": "no-cache",
        })

        # Get cookies first
        session.get(base_url, timeout=10)

        indices = ['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY']

        if symbol.upper() in indices:
            url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol.upper()}"
        else:
            url = f"https://www.nseindia.com/api/option-chain-equities?symbol={symbol.upper()}"

        # retry logic
        for _ in range(3):
            res = session.get(url, timeout=10)

            if res.status_code == 200:
                return res.json()

            elif res.status_code in [401, 403]:
                time.sleep(2)
                continue

            else:
                st.error(f"NSE Error Code: {res.status_code}")
                return None

        st.error("NSE blocked request (try after 1 minute)")
        return None

    except Exception as e:
        st.error(f"Connection Error: {e}")
        return None


# =========================
# PROCESS DATA
# =========================
def process_data(data):
    if not data or "records" not in data:
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
def apply_ai_logic(df):
    if df.empty:
        return df

    df["OI_DIFF"] = df["PE_CHG_OI"] - df["CE_CHG_OI"]

    def signal(row):
        if row["PE_CHG_OI"] > row["CE_CHG_OI"] * 1.8:
            return "🚀 STRONG BUY"
        elif row["CE_CHG_OI"] > row["PE_CHG_OI"] * 1.8:
            return "📉 STRONG SELL"
        else:
            return "⚖️ NEUTRAL"

    df["AI_SIGNAL"] = df.apply(signal, axis=1)
    return df


# =========================
# UI
# =========================
symbol = st.sidebar.selectbox(
    "Select Symbol",
    ["NIFTY", "BANKNIFTY", "FINNIFTY", "RELIANCE", "SBIN"]
)

if st.button("🔄 FETCH AI SIGNALS"):
    with st.spinner("Fetching NSE Data..."):

        raw = fetch_nse(symbol)
        df = process_data(raw)

        if not df.empty:
            df = apply_ai_logic(df)

            # ===== METRICS =====
            total_ce = df["CE_OI"].sum()
            total_pe = df["PE_OI"].sum()
            pcr = total_pe / total_ce if total_ce != 0 else 0

            col1, col2, col3 = st.columns(3)
            col1.metric("Total CE OI", f"{total_ce:,}")
            col2.metric("Total PE OI", f"{total_pe:,}")
            col3.metric("PCR", round(pcr, 2))

            if pcr > 1.2:
                st.success("🔥 VERY BULLISH MARKET")
            elif pcr < 0.8:
                st.error("📉 VERY BEARISH MARKET")
            else:
                st.warning("⚖️ SIDEWAYS MARKET")

            # ===== SIGNALS =====
            st.subheader("🔥 ACTIVE AI SIGNALS")
            signals = df[df["AI_SIGNAL"] != "⚖️ NEUTRAL"]
            st.dataframe(signals[["Strike", "AI_SIGNAL", "CE_LTP", "PE_LTP", "OI_DIFF"]].head(15))

            # ===== FULL TABLE =====
            st.subheader("📊 FULL OPTION CHAIN")
            st.dataframe(df)

        else:
            st.warning("Data not loaded. NSE blocking or market closed.")

st.markdown("---")
st.caption("⚠️ Educational purpose only. Trading involves risk.")
