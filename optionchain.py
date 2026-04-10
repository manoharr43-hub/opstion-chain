import streamlit as st
import pandas as pd
from nsepython import option_chain
from streamlit_autorefresh import st_autorefresh

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="ULTRA NSE AI OPTION CHAIN V3", layout="wide")
st.title("🔥 ULTRA NSE AI OPTION CHAIN V3 (STABLE + NO BLOCK)")

# refresh every 60 sec
st_autorefresh(interval=60000, key="refresh")

# =========================
# FETCH DATA (STABLE API)
# =========================
def fetch_data(symbol):
    try:
        data = option_chain(symbol.upper())
        return data
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
def ai_engine(df):
    if df.empty:
        return df

    def signal(row):
        if row["PE_CHG_OI"] > row["CE_CHG_OI"] * 1.7:
            return "🚀 STRONG BUY"
        elif row["CE_CHG_OI"] > row["PE_CHG_OI"] * 1.7:
            return "📉 STRONG SELL"
        else:
            return "⚖️ NEUTRAL"

    df["SIGNAL"] = df.apply(signal, axis=1)
    df["OI_DIFF"] = df["PE_CHG_OI"] - df["CE_CHG_OI"]
    return df


# =========================
# UI
# =========================
symbol = st.sidebar.selectbox(
    "Select Symbol",
    ["NIFTY", "BANKNIFTY", "FINNIFTY"]
)

if st.button("🔥 GET LIVE AI SIGNALS"):

    with st.spinner("Fetching live NSE data..."):
        data = fetch_data(symbol)
        df = process_data(data)

        if not df.empty:

            df = ai_engine(df)

            # =========================
            # MARKET SUMMARY
            # =========================
            ce_total = df["CE_OI"].sum()
            pe_total = df["PE_OI"].sum()
            pcr = pe_total / ce_total if ce_total else 0

            col1, col2, col3 = st.columns(3)
            col1.metric("CE OI", f"{ce_total:,}")
            col2.metric("PE OI", f"{pe_total:,}")
            col3.metric("PCR", round(pcr, 2))

            if pcr > 1.2:
                st.success("🔥 STRONG BULLISH MARKET")
            elif pcr < 0.8:
                st.error("📉 STRONG BEARISH MARKET")
            else:
                st.warning("⚖️ SIDEWAYS MARKET")

            # =========================
            # TOP SIGNALS
            # =========================
            st.subheader("🔥 TOP AI SIGNALS")
            signals = df[df["SIGNAL"] != "⚖️ NEUTRAL"]
            st.dataframe(signals.sort_values("OI_DIFF", ascending=False).head(15))

            # =========================
            # FULL DATA
            # =========================
            st.subheader("📊 FULL OPTION CHAIN")
            st.dataframe(df)

        else:
            st.error("❌ No data received (try again after some time)")

st.markdown("---")
st.caption("⚠️ Educational tool only. Not financial advice.")
