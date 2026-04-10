import streamlit as st
import yfinance as yf
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="AI STOCK SCANNER", layout="wide")
st.title("🔥 AI STOCK SCANNER (100% STABLE VERSION)")

st_autorefresh(interval=120000, key="refresh")

# =========================
# FETCH DATA (YAHOO FINANCE)
# =========================
def fetch_data(symbol):
    try:
        df = yf.download(symbol + ".NS", period="5d", interval="15m")
        return df
    except Exception as e:
        st.error(f"Fetch Error: {e}")
        return None


# =========================
# AI SIGNAL ENGINE
# =========================
def ai_signals(df):
    if df is None or df.empty:
        return df

    df = df.copy()

    df["EMA_5"] = df["Close"].ewm(span=5).mean()
    df["EMA_20"] = df["Close"].ewm(span=20).mean()

    def signal(row):
        if row["EMA_5"] > row["EMA_20"]:
            return "🚀 BUY (UPTREND)"
        else:
            return "📉 SELL (DOWNTREND)"

    df["SIGNAL"] = df.apply(signal, axis=1)

    return df


# =========================
# UI
# =========================
symbol = st.sidebar.selectbox(
    "Select Stock",
    ["RELIANCE", "TCS", "INFY", "SBIN", "HDFCBANK", "NIFTY"]
)

if st.button("🔥 GET AI SIGNALS"):

    with st.spinner("Analyzing Market..."):

        df = fetch_data(symbol)

        if df is not None and not df.empty:

            df = ai_signals(df)

            # =========================
            # METRICS
            # =========================
            last = df.iloc[-1]

            col1, col2, col3 = st.columns(3)
            col1.metric("Close Price", round(last["Close"], 2))
            col2.metric("EMA 5", round(last["EMA_5"], 2))
            col3.metric("EMA 20", round(last["EMA_20"], 2))

            # =========================
            # SIGNAL
            # =========================
            st.subheader("🔥 LIVE SIGNAL")
            st.success(last["SIGNAL"])

            # =========================
            # CHART DATA
            # =========================
            st.subheader("📊 PRICE DATA")
            st.dataframe(df.tail(50))

        else:
            st.error("❌ Data not available")

st.markdown("---")
st.caption("⚠️ Educational purpose only. Not financial advice.")
