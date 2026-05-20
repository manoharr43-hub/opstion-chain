# =========================================================
# 🚀 NSE AI PRO MAX V3.0 - FINAL STABLE INSTITUTIONAL BUILD
# =========================================================

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time

from concurrent.futures import ThreadPoolExecutor

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="NSE AI PRO MAX V3.0",
    page_icon="🚀",
    layout="wide"
)

# =========================================================
# AUTO REFRESH
# =========================================================

if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

if time.time() - st.session_state.last_refresh > 60:
    st.session_state.last_refresh = time.time()
    st.rerun()

# =========================================================
# DARK MODE CSS
# =========================================================

st.markdown("""
<style>

.main {
    background-color: #0E1117;
    color: white;
}

.stMetric {
    background: #1E1E1E;
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #333;
}

[data-testid="stSidebar"] {
    background-color: #161A28;
}

h1,h2,h3,h4 {
    color: white;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# TITLE
# =========================================================

st.title("🚀 NSE AI PRO MAX V3.0")
st.caption("INSTITUTIONAL EDITION")

# =========================================================
# NSE STOCK LIST
# =========================================================

nse_stocks = {
    "RELIANCE": "RELIANCE.NS",
    "HDFCBANK": "HDFCBANK.NS",
    "ICICIBANK": "ICICIBANK.NS",
    "INFY": "INFY.NS",
    "TCS": "TCS.NS",
    "SBIN": "SBIN.NS",
    "ITC": "ITC.NS",
    "LT": "LT.NS",
    "AXISBANK": "AXISBANK.NS",
    "KOTAKBANK": "KOTAKBANK.NS",
    "SUNPHARMA": "SUNPHARMA.NS",
    "BAJFINANCE": "BAJFINANCE.NS"
}

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("⚙️ SETTINGS")

selected_stock = st.sidebar.selectbox(
    "SELECT STOCK",
    list(nse_stocks.keys())
)

interval = st.sidebar.selectbox(
    "INTERVAL",
    ["5m", "15m", "30m", "1h"]
)

period = st.sidebar.selectbox(
    "PERIOD",
    ["1d", "5d", "1mo"]
)

ticker = nse_stocks[selected_stock]

# =========================================================
# INDICATOR FUNCTION
# =========================================================

def calculate_indicators(df):

    # -----------------------------------------------------
    # FIX MULTI INDEX
    # -----------------------------------------------------

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # -----------------------------------------------------
    # FORCE 1D SERIES
    # -----------------------------------------------------

    for col in ["Close", "High", "Low", "Open", "Volume"]:
        df[col] = pd.Series(df[col]).squeeze()

    # -----------------------------------------------------
    # EMA
    # -----------------------------------------------------

    df["EMA20"] = df["Close"].ewm(span=20).mean()
    df["EMA50"] = df["Close"].ewm(span=50).mean()

    # -----------------------------------------------------
    # RSI
    # -----------------------------------------------------

    delta = df["Close"].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss

    df["RSI"] = 100 - (100 / (1 + rs))

    # -----------------------------------------------------
    # MACD
    # -----------------------------------------------------

    ema12 = df["Close"].ewm(span=12).mean()
    ema26 = df["Close"].ewm(span=26).mean()

    df["MACD"] = ema12 - ema26
    df["MACD_SIGNAL"] = df["MACD"].ewm(span=9).mean()

    # -----------------------------------------------------
    # VWAP
    # -----------------------------------------------------

    df["VWAP"] = (
        (df["Close"] * df["Volume"]).cumsum()
        / df["Volume"].cumsum()
    )

    # -----------------------------------------------------
    # ATR
    # -----------------------------------------------------

    high_low = df["High"] - df["Low"]

    high_close = np.abs(
        df["High"] - df["Close"].shift()
    )

    low_close = np.abs(
        df["Low"] - df["Close"].shift()
    )

    ranges = pd.concat(
        [high_low, high_close, low_close],
        axis=1
    )

    true_range = ranges.max(axis=1)

    df["ATR"] = true_range.rolling(14).mean()

    # -----------------------------------------------------
    # VOLUME SPIKE
    # -----------------------------------------------------

    df["AVG_VOLUME"] = df["Volume"].rolling(20).mean()

    df["VOLUME_SPIKE"] = np.where(
        df["Volume"] > df["AVG_VOLUME"] * 1.5,
        "YES",
        "NO"
    )

    df = df.fillna(0)

    return df

# =========================================================
# AI SIGNAL ENGINE
# =========================================================

def generate_signal(df):

    latest = df.iloc[-1]

    score = 0

    # EMA TREND
    if latest["EMA20"] > latest["EMA50"]:
        score += 25
    else:
        score -= 25

    # VWAP
    if latest["Close"] > latest["VWAP"]:
        score += 20
    else:
        score -= 20

    # RSI
    if 55 < latest["RSI"] < 70:
        score += 20

    elif latest["RSI"] > 75:
        score -= 10

    elif latest["RSI"] < 30:
        score += 15

    # MACD
    if latest["MACD"] > latest["MACD_SIGNAL"]:
        score += 25
    else:
        score -= 25

    # VOLUME
    if latest["VOLUME_SPIKE"] == "YES":
        score += 10

    # FINAL SIGNAL
    if score >= 70:
        signal = "🚀 STRONG BUY"

    elif score >= 30:
        signal = "✅ BUY"

    elif score <= -70:
        signal = "🚨 STRONG SELL"

    elif score <= -30:
        signal = "🔻 SELL"

    else:
        signal = "⚠️ SIDEWAYS"

    return signal, score

# =========================================================
# DOWNLOAD DATA
# =========================================================

try:

    df = yf.download(
        ticker,
        interval=interval,
        period=period,
        progress=False,
        auto_adjust=True,
        group_by='column'
    )

    if df.empty:

        st.error("NO DATA FOUND")

    else:

        df = calculate_indicators(df)

        signal, score = generate_signal(df)

        latest = df.iloc[-1]

        current_price = float(latest["Close"])

        # =================================================
        # SIGNAL DISPLAY
        # =================================================

        st.subheader("🤖 AI SIGNAL ENGINE")

        if "BUY" in signal:
            st.success(f"{signal} | SCORE : {score}")

        elif "SELL" in signal:
            st.error(f"{signal} | SCORE : {score}")

        else:
            st.warning(f"{signal} | SCORE : {score}")

        # =================================================
        # METRICS
        # =================================================

        c1, c2, c3, c4, c5 = st.columns(5)

        c1.metric(
            "PRICE",
            f"₹ {round(current_price,2)}"
        )

        c2.metric(
            "RSI",
            round(float(latest["RSI"]),2)
        )

        c3.metric(
            "VWAP",
            round(float(latest["VWAP"]),2)
        )

        c4.metric(
            "MACD",
            round(float(latest["MACD"]),2)
        )

        c5.metric(
            "AI SCORE",
            score
        )

        # =================================================
        # ATR TARGET ENGINE
        # =================================================

        atr = float(latest["ATR"])

        entry = current_price

        sl = entry - atr

        target1 = entry + atr

        target2 = entry + (atr * 2)

        target3 = entry + (atr * 3)

        st.markdown("---")

        st.subheader("🎯 AI TARGET ENGINE")

        t1, t2, t3, t4, t5 = st.columns(5)

        t1.metric("ENTRY", round(entry,2))
        t2.metric("STOPLOSS", round(sl,2))
        t3.metric("TARGET 1", round(target1,2))
        t4.metric("TARGET 2", round(target2,2))
        t5.metric("TARGET 3", round(target3,2))

        # =================================================
        # VOLUME SPIKE
        # =================================================

        st.markdown("---")

        if latest["VOLUME_SPIKE"] == "YES":
            st.success("🔥 VOLUME BLAST DETECTED")
        else:
            st.info("NORMAL VOLUME")

        # =================================================
        # LIVE CHART
        # =================================================

        st.markdown("---")

        st.subheader(f"📈 {selected_stock} LIVE CHART")

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["Close"],
                mode="lines",
                name="Close"
            )
        )

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["EMA20"],
                mode="lines",
                name="EMA20"
            )
        )

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["EMA50"],
                mode="lines",
                name="EMA50"
            )
        )

        fig.update_layout(
            template="plotly_dark",
            height=650,
            xaxis_rangeslider_visible=False
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # =================================================
        # AI SCANNER
        # =================================================

        st.markdown("---")

        st.subheader("🔥 LIVE NSE AI SCANNER")

        def scan_stock(item):

            name, tick = item

            try:

                data = yf.download(
                    tick,
                    interval=interval,
                    period=period,
                    progress=False,
                    auto_adjust=True
                )

                if data.empty:
                    return None

                data = calculate_indicators(data)

                sig, scr = generate_signal(data)

                last = data.iloc[-1]

                return {
                    "STOCK": name,
                    "PRICE": round(float(last["Close"]),2),
                    "SIGNAL": sig,
                    "SCORE": scr,
                    "RSI": round(float(last["RSI"]),2)
                }

            except:
                return None

        results = []

        with ThreadPoolExecutor(max_workers=10) as executor:

            scanned = executor.map(
                scan_stock,
                nse_stocks.items()
            )

        for item in scanned:

            if item is not None:
                results.append(item)

        scan_df = pd.DataFrame(results)

        scan_df = scan_df.sort_values(
            by="SCORE",
            ascending=False
        )

        st.dataframe(
            scan_df,
            use_container_width=True,
            hide_index=True
        )

        # =================================================
        # TOP PICKS
        # =================================================

        st.markdown("---")

        st.subheader("🚀 TOP AI PICKS")

        top_buys = scan_df[
            scan_df["SIGNAL"].str.contains("BUY")
        ].head(5)

        st.dataframe(
            top_buys,
            use_container_width=True,
            hide_index=True
        )

# =========================================================
# ERROR HANDLING
# =========================================================

except Exception as e:

    st.error(f"ERROR : {str(e)}")

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "🚀 NSE AI PRO MAX V3.0 | Institutional Edition"
)
