import streamlit as st
import yfinance as yf
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="SAFE AI TRADING SYSTEM", layout="wide")
st.title("🔥 SAFE AI TRADING SYSTEM (OLD CODE SAFE + NEW MODULE)")

st_autorefresh(interval=120000, key="refresh_safe")

# =========================
# SAFE DATA FETCH (NO NSE)
# =========================
def get_market_data(symbol):
    try:
        df = yf.download(
            symbol + ".NS",
            period="5d",
            interval="15m",
            progress=False,
            threads=False
        )

        if df is None or df.empty:
            return None

        return df

    except:
        return None


# =========================
# AI ENGINE (SAFE VERSION)
# =========================
def ai_engine(df):
    df = df.copy()
    df = df.dropna()

    # indicators
    df["EMA_5"] = df["Close"].ewm(span=5).mean()
    df["EMA_20"] = df["Close"].ewm(span=20).mean()
    df["EMA_50"] = df["Close"].ewm(span=50).mean()

    # default
    df["SIGNAL"] = "⚖️ SIDEWAYS"

    # BUY condition
    buy = (df["EMA_5"] > df["EMA_20"]) & (df["EMA_20"] > df["EMA_50"])

    # SELL condition
    sell = (df["EMA_5"] < df["EMA_20"]) & (df["EMA_20"] < df["EMA_50"])

    df.loc[buy, "SIGNAL"] = "🚀 BUY"
    df.loc[sell, "SIGNAL"] = "📉 SELL"

    return df


# =========================
# UI
# =========================
symbol = st.sidebar.selectbox(
    "Select Stock",
    ["RELIANCE", "TCS", "INFY", "SBIN", "HDFCBANK", "ICICIBANK"]
)

if st.button("🔥 RUN SAFE ANALYSIS"):

    st.info("Analyzing market safely...")

    df = get_market_data(symbol)

    if df is None:
        st.error("❌ Data not available (fallback mode active)")
    else:
        df = ai_engine(df)

        last = df.iloc[-1]

        # =========================
        # METRICS
        # =========================
        col1, col2, col3 = st.columns(3)

        col1.metric("Close", round(last["Close"], 2))
        col2.metric("EMA 20", round(last["EMA_20"], 2))
        col3.metric("EMA 50", round(last["EMA_50"], 2))

        # =========================
        # SIGNAL
        # =========================
        st.subheader("🔥 LIVE SIGNAL")
        st.success(last["SIGNAL"])

        # =========================
        # TABLE
        # =========================
        st.subheader("📊 DATA VIEW")
        st.dataframe(df.tail(50))

# =========================
# FOOTER
# =========================
st.markdown("---")
st.caption("✔ SAFE MODULE VERSION | ✔ NO NSE BLOCK | ✔ OLD CODE NOT MODIFIED")
