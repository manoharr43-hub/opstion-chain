import streamlit as st
import yfinance as yf
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="FINAL AI SCANNER", layout="wide")
st.title("🔥 FINAL AI STOCK SCANNER (CRASH FREE VERSION)")

st_autorefresh(interval=120000, key="refresh")

# =========================
# DATA FETCH
# =========================
def get_data(symbol):
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

    except Exception:
        return None


# =========================
# AI ENGINE (FIXED - NO APPLY ERROR)
# =========================
def ai_engine(df):
    df = df.copy()

    # remove bad data
    df = df.dropna()

    # indicators
    df["EMA_5"] = df["Close"].ewm(span=5).mean()
    df["EMA_20"] = df["Close"].ewm(span=20).mean()
    df["EMA_50"] = df["Close"].ewm(span=50).mean()

    # default signal
    df["SIGNAL"] = "⚖️ SIDEWAYS"

    # BUY condition
    buy_condition = (
        (df["EMA_5"] > df["EMA_20"]) &
        (df["EMA_20"] > df["EMA_50"])
    )

    # SELL condition
    sell_condition = (
        (df["EMA_5"] < df["EMA_20"]) &
        (df["EMA_20"] < df["EMA_50"])
    )

    df.loc[buy_condition, "SIGNAL"] = "🚀 STRONG BUY"
    df.loc[sell_condition, "SIGNAL"] = "📉 STRONG SELL"

    return df


# =========================
# UI
# =========================
symbol = st.sidebar.selectbox(
    "Select Stock",
    ["RELIANCE", "TCS", "INFY", "SBIN", "HDFCBANK", "ICICIBANK", "NIFTY"]
)

if st.button("🔥 GET AI SIGNALS"):

    st.info("Fetching market data...")

    df = get_data(symbol)

    if df is None:
        st.error("❌ No data received. Try again later.")
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
        # DATA
        # =========================
        st.subheader("📊 MARKET DATA")
        st.dataframe(df.tail(50))

st.markdown("---")
st.caption("⚠️ Educational purpose only. Not financial advice.")
