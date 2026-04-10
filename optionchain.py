import streamlit as st
import yfinance as yf
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="FINAL AI TRADING SCANNER", layout="wide")
st.title("🔥 FINAL AI STOCK SCANNER (STABLE + NO ERROR)")

st_autorefresh(interval=120000, key="refresh")

# =========================
# FETCH DATA
# =========================
def get_data(symbol):
    try:
        ticker = symbol + ".NS"

        df = yf.download(
            ticker,
            period="5d",
            interval="15m",
            progress=False,
            threads=False
        )

        if df is None or df.empty:
            return None

        return df

    except Exception:
        return None


# =========================
# AI ENGINE
# =========================
def ai_engine(df):
    df = df.copy()

    df["EMA_5"] = df["Close"].ewm(span=5).mean()
    df["EMA_20"] = df["Close"].ewm(span=20).mean()
    df["EMA_50"] = df["Close"].ewm(span=50).mean()

    def signal(row):
        if row["EMA_5"] > row["EMA_20"] > row["EMA_50"]:
            return "🚀 STRONG BUY"
        elif row["EMA_5"] < row["EMA_20"] < row["EMA_50"]:
            return "📉 STRONG SELL"
        else:
            return "⚖️ SIDEWAYS"

    df["SIGNAL"] = df.apply(signal, axis=1)

    return df


# =========================
# UI
# =========================
symbol = st.sidebar.selectbox(
    "Select Stock",
    ["RELIANCE", "TCS", "INFY", "SBIN", "HDFCBANK", "ICICIBANK", "NIFTY"]
)

if st.button("🔥 GET LIVE AI SIGNALS"):

    st.info("Fetching market data...")

    df = get_data(symbol)

    if df is None:
        st.error("❌ No data available. Try again after 1 minute.")
    else:
        df = ai_engine(df)

        last = df.iloc[-1]

        # =========================
        # METRICS
        # =========================
        col1, col2, col3 = st.columns(3)

        col1.metric("Close Price", round(last["Close"], 2))
        col2.metric("EMA 20", round(last["EMA_20"], 2))
        col3.metric("EMA 50", round(last["EMA_50"], 2))

        # =========================
        # SIGNAL
        # =========================
        st.subheader("🔥 LIVE AI SIGNAL")
        st.success(last["SIGNAL"])

        # =========================
        # CHART DATA
        # =========================
        st.subheader("📊 MARKET DATA")
        st.dataframe(df.tail(50))

st.markdown("---")
st.caption("⚠️ Educational purpose only. Not financial advice.")
