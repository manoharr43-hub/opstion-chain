# =========================================================
# 🚀 NSE AI PRO MAX V4.0 - ULTRA STABLE EDITION
# =========================================================

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
import io
import pytz
from datetime import datetime

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="NSE AI PRO MAX V4.0",
    page_icon="🚀",
    layout="wide"
)

# =========================================================
# DARK UI
# =========================================================

st.markdown("""
<style>

.main {
    background-color: #0E1117;
    color: white;
}

[data-testid="stSidebar"] {
    background-color: #111827;
}

.stMetric {
    background-color: #1F2937;
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #333;
}

h1,h2,h3,h4,h5 {
    color: white;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# TITLE
# =========================================================

st.title("🚀 NSE AI PRO MAX V4.0")
st.caption("Institutional AI Trading Dashboard + Smart Option Chain Analyzer")

# =========================================================
# NSE STOCK LIST
# =========================================================

nse_stocks = {
    "RELIANCE": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "INFY": "INFY.NS",
    "HDFCBANK": "HDFCBANK.NS",
    "ICICIBANK": "ICICIBANK.NS",
    "SBIN": "SBIN.NS",
    "LT": "LT.NS",
    "ITC": "ITC.NS",
    "AXISBANK": "AXISBANK.NS",
    "KOTAKBANK": "KOTAKBANK.NS",
    "BAJFINANCE": "BAJFINANCE.NS",
    "SUNPHARMA": "SUNPHARMA.NS",
    "MARUTI": "MARUTI.NS",
    "HINDUNILVR": "HINDUNILVR.NS"
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

st.sidebar.markdown("---")

st.sidebar.subheader("📌 APP STATUS")

india = pytz.timezone('Asia/Kolkata')
current_time = datetime.now(india)

st.sidebar.success(f"🟢 LIVE")
st.sidebar.info(f"{current_time.strftime('%d-%m-%Y %H:%M:%S')}")

# =========================================================
# AUTO REFRESH
# =========================================================

if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

if time.time() - st.session_state.last_refresh > 60:
    st.session_state.last_refresh = time.time()
    st.rerun()

# =========================================================
# INDICATORS
# =========================================================

def calculate_indicators(df):

    df["EMA20"] = df["Close"].ewm(span=20).mean()

    df["EMA50"] = df["Close"].ewm(span=50).mean()

    delta = df["Close"].diff()

    gain = delta.clip(lower=0)

    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()

    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss

    df["RSI"] = 100 - (100 / (1 + rs))

    ema12 = df["Close"].ewm(span=12).mean()

    ema26 = df["Close"].ewm(span=26).mean()

    df["MACD"] = ema12 - ema26

    df["MACD_SIGNAL"] = df["MACD"].ewm(span=9).mean()

    df["VWAP"] = (
        (df["Close"] * df["Volume"]).cumsum()
        /
        df["Volume"].cumsum()
    )

    df.fillna(0, inplace=True)

    return df

# =========================================================
# SIGNAL ENGINE
# =========================================================

def generate_signal(df):

    latest = df.iloc[-1]

    score = 0

    # EMA
    if latest["EMA20"] > latest["EMA50"]:
        score += 25
    else:
        score -= 25

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

    # VWAP
    if latest["Close"] > latest["VWAP"]:
        score += 20
    else:
        score -= 20

    # FINAL
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
# TABS
# =========================================================

tab1, tab2 = st.tabs([
    "📈 AI LIVE CHART",
    "📂 OPTION CHAIN ANALYZER"
])

# =========================================================
# TAB 1
# =========================================================

with tab1:

    try:

        data = yf.download(
            ticker,
            interval=interval,
            period=period,
            progress=False,
            auto_adjust=True
        )

        if not data.empty:

            data = calculate_indicators(data)

            signal, score = generate_signal(data)

            latest = data.iloc[-1]

            st.subheader("🤖 AI SIGNAL ENGINE")

            if "BUY" in signal:
                st.success(f"{signal} | AI SCORE : {score}")

            elif "SELL" in signal:
                st.error(f"{signal} | AI SCORE : {score}")

            else:
                st.warning(f"{signal} | AI SCORE : {score}")

            c1, c2, c3, c4, c5 = st.columns(5)

            c1.metric(
                "PRICE",
                f"₹ {round(float(latest['Close']),2)}"
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

            st.markdown("---")

            st.subheader(f"📈 {selected_stock} LIVE CHART")

            fig = go.Figure()

            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data["Close"],
                    mode='lines',
                    name='Close Price'
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data["EMA20"],
                    mode='lines',
                    name='EMA20'
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data["EMA50"],
                    mode='lines',
                    name='EMA50'
                )
            )

            fig.update_layout(
                template="plotly_dark",
                height=500
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    except Exception as e:

        st.error(f"LIVE DATA ERROR : {str(e)}")

# =========================================================
# TAB 2
# =========================================================

with tab2:

    st.header("📂 AI OPTION CHAIN ANALYZER")

    st.write(
        "Upload NSE option chain CSV / Excel file."
    )

    uploaded_file = st.file_uploader(
        "Upload File",
        type=["csv", "xlsx", "xls"]
    )

    if uploaded_file is not None:

        try:

            raw_df = None

            # =================================================
            # CSV READER
            # =================================================

            if uploaded_file.name.endswith(".csv"):

                encodings = [
                    "utf-8",
                    "latin-1",
                    "cp1252"
                ]

                for enc in encodings:

                    try:

                        uploaded_file.seek(0)

                        raw_df = pd.read_csv(
                            uploaded_file,
                            engine='python',
                            encoding=enc,
                            on_bad_lines='skip'
                        )

                        break

                    except:
                        continue

            # =================================================
            # EXCEL READER
            # =================================================

            else:

                raw_df = pd.read_excel(
                    uploaded_file,
                    engine="openpyxl"
                )

            # =================================================
            # VALIDATION
            # =================================================

            if raw_df is not None and not raw_df.empty:

                raw_df.dropna(
                    how='all',
                    inplace=True
                )

                raw_df.dropna(
                    how='all',
                    axis=1,
                    inplace=True
                )

                st.success("✅ FILE LOADED SUCCESSFULLY")

                st.subheader("📊 DATA PREVIEW")

                st.dataframe(
                    raw_df.head(20),
                    use_container_width=True
                )

                # =============================================
                # AI ANALYSIS BUTTON
                # =============================================

                if st.button(
                    "🚀 RUN AI ANALYSIS",
                    use_container_width=True
                ):

                    numeric_df = raw_df.apply(
                        pd.to_numeric,
                        errors='coerce'
                    )

                    numeric_df.fillna(
                        0,
                        inplace=True
                    )

                    # =========================================
                    # COLUMN ANALYSIS
                    # =========================================

                    col_sums = numeric_df.sum()

                    strongest_col = col_sums.idxmax()

                    strongest_value = col_sums.max()

                    weakest_col = col_sums.idxmin()

                    weakest_value = col_sums.min()

                    # =========================================
                    # AI TARGETS
                    # =========================================

                    buy_target = strongest_value * 1.15

                    sell_target = abs(weakest_value) * 0.85

                    # =========================================
                    # RESULT UI
                    # =========================================

                    st.subheader("🤖 AI ANALYSIS REPORT")

                    a1, a2, a3, a4 = st.columns(4)

                    a1.metric(
                        "STRONGEST COLUMN",
                        strongest_col
                    )

                    a2.metric(
                        "MOMENTUM",
                        round(strongest_value, 2)
                    )

                    a3.metric(
                        "BUY TARGET",
                        round(buy_target, 2)
                    )

                    a4.metric(
                        "SELL TARGET",
                        round(sell_target, 2)
                    )

                    # =========================================
                    # AI SIGNAL
                    # =========================================

                    if strongest_value > abs(weakest_value):

                        st.success(
                            "🚀 AI SIGNAL : BULLISH MOMENTUM DETECTED"
                        )

                    else:

                        st.error(
                            "🔻 AI SIGNAL : BEARISH MOMENTUM DETECTED"
                        )

                    # =========================================
                    # CHART
                    # =========================================

                    fig2 = go.Figure()

                    fig2.add_trace(
                        go.Bar(
                            x=col_sums.index.astype(str),
                            y=col_sums.values,
                            name="Volume Strength"
                        )
                    )

                    fig2.update_layout(
                        template="plotly_dark",
                        height=450,
                        title="AI OPTION CHAIN STRENGTH"
                    )

                    st.plotly_chart(
                        fig2,
                        use_container_width=True
                    )

            else:

                st.error(
                    "❌ FILE EMPTY OR INVALID"
                )

        except Exception as e:

            st.error(
                f"❌ PROCESSING ERROR : {str(e)}"
            )

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "🚀 NSE AI PRO MAX V4.0 | Institutional Trading System"
)
