# =========================================================
# 🚀 NSE AI PRO MAX V5.0 - INSTITUTIONAL LIVE ENGINE
# =========================================================

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go
import pytz
from datetime import datetime

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="NSE AI PRO MAX V5.0",
    page_icon="🚀",
    layout="wide"
)

# =========================================================
# CUSTOM CSS
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
    border: 1px solid #374151;
    border-radius: 12px;
    padding: 15px;
}

h1,h2,h3,h4 {
    color: white !important;
}

div.stButton > button:first-child {
    background-color: #2563EB;
    color: white;
    border-radius: 8px;
    border: none;
    width: 100%;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# TITLE
# =========================================================

st.title("🚀 NSE AI PRO MAX V5.0")
st.caption("Institutional AI Trading + Live Option Chain System")

# =========================================================
# NSE STOCK DATABASE
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
    "HINDUNILVR": "HINDUNILVR.NS",
    "NIFTY 50": "^NSEI",
    "BANKNIFTY": "^NSEBANK"
}

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("⚙️ CONTROL PANEL")

selected_stock = st.sidebar.selectbox(
    "SELECT STOCK",
    list(nse_stocks.keys())
)

interval = st.sidebar.selectbox(
    "SELECT INTERVAL",
    ["5m", "15m", "30m", "1h"]
)

period = st.sidebar.selectbox(
    "SELECT PERIOD",
    ["1d", "5d", "1mo"]
)

ticker = nse_stocks[selected_stock]

# =========================================================
# TIME
# =========================================================

india = pytz.timezone("Asia/Kolkata")

st.sidebar.info(
    datetime.now(india).strftime(
        "🕒 %d-%m-%Y %H:%M:%S IST"
    )
)

# =========================================================
# MARKET STATUS
# =========================================================

hour = datetime.now(india).hour

if 9 <= hour <= 15:
    st.sidebar.success("🟢 MARKET OPEN")
else:
    st.sidebar.error("🔴 MARKET CLOSED")

# =========================================================
# CACHE MARKET DATA
# =========================================================

@st.cache_data(ttl=60)

def load_market_data(ticker, interval, period):

    data = yf.download(
        ticker,
        interval=interval,
        period=period,
        progress=False,
        auto_adjust=True,
        threads=True
    )

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    return data

# =========================================================
# TECHNICAL INDICATORS
# =========================================================

def add_indicators(df):

    df = df.copy()

    # EMA

    df["EMA20"] = df["Close"].ewm(
        span=20,
        adjust=False
    ).mean()

    df["EMA50"] = df["Close"].ewm(
        span=50,
        adjust=False
    ).mean()

    # RSI

    delta = df["Close"].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / (avg_loss + 1e-10)

    df["RSI"] = 100 - (100 / (1 + rs))

    # MACD

    ema12 = df["Close"].ewm(span=12).mean()
    ema26 = df["Close"].ewm(span=26).mean()

    df["MACD"] = ema12 - ema26

    df["MACD_SIGNAL"] = df["MACD"].ewm(span=9).mean()

    # VWAP

    df["VWAP"] = (
        (df["Close"] * df["Volume"]).cumsum()
        /
        (df["Volume"].cumsum() + 1e-10)
    )

    # VOLUME SPIKE

    df["VOL_AVG"] = df["Volume"].rolling(20).mean()

    df["VOLUME_SPIKE"] = (
        df["Volume"] > df["VOL_AVG"] * 2
    )

    df.fillna(0, inplace=True)

    return df

# =========================================================
# AI SIGNAL ENGINE
# =========================================================

def ai_signal(latest):

    score = 0

    # EMA

    if latest["EMA20"] > latest["EMA50"]:
        score += 25
    else:
        score -= 25

    # RSI

    if 55 <= latest["RSI"] <= 70:
        score += 20

    elif latest["RSI"] < 30:
        score += 15

    elif latest["RSI"] > 75:
        score -= 15

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

    # VOLUME

    if latest["VOLUME_SPIKE"]:
        score += 10

    # SIGNAL

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

    confidence = min(abs(score), 95)

    return signal, score, confidence

# =========================================================
# LIVE OPTION CHAIN API
# =========================================================

@st.cache_data(ttl=60)

def get_option_chain(symbol="NIFTY"):

    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"

    headers = {
        "user-agent": "Mozilla/5.0"
    }

    session = requests.Session()

    session.get(
        "https://www.nseindia.com",
        headers=headers
    )

    response = session.get(
        url,
        headers=headers
    )

    data = response.json()

    records = data["records"]["data"]

    rows = []

    for item in records:

        strike = item.get("strikePrice", 0)

        ce = item.get("CE", {})
        pe = item.get("PE", {})

        rows.append({

            "STRIKE": strike,

            "CALL_OI": ce.get("openInterest", 0),
            "CALL_CHG_OI": ce.get("changeinOpenInterest", 0),
            "CALL_VOL": ce.get("totalTradedVolume", 0),

            "PUT_OI": pe.get("openInterest", 0),
            "PUT_CHG_OI": pe.get("changeinOpenInterest", 0),
            "PUT_VOL": pe.get("totalTradedVolume", 0)

        })

    return pd.DataFrame(rows)

# =========================================================
# TABS
# =========================================================

tab1, tab2, tab3 = st.tabs([
    "📈 LIVE TECHNICAL",
    "📂 LIVE OPTION CHAIN",
    "🤖 AI SCANNER"
])

# =========================================================
# TAB 1 - TECHNICAL ANALYSIS
# =========================================================

with tab1:

    try:

        data = load_market_data(
            ticker,
            interval,
            period
        )

        if data.empty:
            st.error("❌ NO MARKET DATA")
            st.stop()

        data = add_indicators(data)

        latest = data.iloc[-1]

        signal, score, confidence = ai_signal(latest)

        # =====================================================
        # SIGNAL DISPLAY
        # =====================================================

        st.subheader("🤖 AI TRADING SIGNAL")

        if "BUY" in signal:
            st.success(
                f"{signal} | CONFIDENCE : {confidence}%"
            )

        elif "SELL" in signal:
            st.error(
                f"{signal} | CONFIDENCE : {confidence}%"
            )

        else:
            st.warning(
                f"{signal} | CONFIDENCE : {confidence}%"
            )

        # =====================================================
        # METRICS
        # =====================================================

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

        # =====================================================
        # CANDLE CHART
        # =====================================================

        fig = go.Figure()

        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data["Open"],
            high=data["High"],
            low=data["Low"],
            close=data["Close"],
            name="PRICE"
        ))

        fig.add_trace(go.Scatter(
            x=data.index,
            y=data["EMA20"],
            mode="lines",
            name="EMA20"
        ))

        fig.add_trace(go.Scatter(
            x=data.index,
            y=data["EMA50"],
            mode="lines",
            name="EMA50"
        ))

        fig.update_layout(
            template="plotly_dark",
            height=650,
            xaxis_rangeslider_visible=False
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # =====================================================
        # SMART MONEY DETECTOR
        # =====================================================

        spike = latest["VOLUME_SPIKE"]

        st.subheader("🏦 SMART MONEY TRACKER")

        if spike:
            st.success(
                "🔥 INSTITUTIONAL VOLUME DETECTED"
            )
        else:
            st.info(
                "Normal Market Participation"
            )

    except Exception as e:

        st.error(f"🔴 ERROR : {e}")

# =========================================================
# TAB 2 - LIVE OPTION CHAIN
# =========================================================

with tab2:

    st.header("📂 LIVE NSE OPTION CHAIN")

    option_symbol = st.selectbox(
        "SELECT OPTION INDEX",
        ["NIFTY", "BANKNIFTY"]
    )

    try:

        option_df = get_option_chain(option_symbol)

        if option_df.empty:
            st.error("❌ NO OPTION DATA")
            st.stop()

        # =====================================================
        # PCR
        # =====================================================

        total_call = option_df["CALL_OI"].sum()
        total_put = option_df["PUT_OI"].sum()

        pcr = (
            total_put / total_call
            if total_call > 0
            else 0
        )

        # =====================================================
        # SUPPORT / RESISTANCE
        # =====================================================

        resistance = option_df.loc[
            option_df["CALL_OI"].idxmax(),
            "STRIKE"
        ]

        support = option_df.loc[
            option_df["PUT_OI"].idxmax(),
            "STRIKE"
        ]

        # =====================================================
        # MAX PAIN
        # =====================================================

        option_df["TOTAL_OI"] = (
            option_df["CALL_OI"]
            +
            option_df["PUT_OI"]
        )

        max_pain = option_df.loc[
            option_df["TOTAL_OI"].idxmax(),
            "STRIKE"
        ]

        # =====================================================
        # SIGNAL
        # =====================================================

        if pcr > 1.15:
            direction = "🚀 BULLISH"

        elif pcr < 0.85:
            direction = "🔻 BEARISH"

        else:
            direction = "⚠️ SIDEWAYS"

        # =====================================================
        # METRICS
        # =====================================================

        st.subheader("🤖 OPTION CHAIN REPORT")

        if "BULLISH" in direction:
            st.success(direction)

        elif "BEARISH" in direction:
            st.error(direction)

        else:
            st.warning(direction)

        m1, m2, m3, m4 = st.columns(4)

        m1.metric(
            "PCR",
            round(pcr,2)
        )

        m2.metric(
            "SUPPORT",
            int(support)
        )

        m3.metric(
            "RESISTANCE",
            int(resistance)
        )

        m4.metric(
            "MAX PAIN",
            int(max_pain)
        )

        # =====================================================
        # OI CHART
        # =====================================================

        fig2 = go.Figure()

        fig2.add_trace(go.Bar(
            x=option_df["STRIKE"],
            y=option_df["CALL_OI"],
            name="CALL OI"
        ))

        fig2.add_trace(go.Bar(
            x=option_df["STRIKE"],
            y=option_df["PUT_OI"],
            name="PUT OI"
        ))

        fig2.update_layout(
            template="plotly_dark",
            barmode="group",
            height=650,
            title="LIVE OPEN INTEREST"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

        # =====================================================
        # OI CHANGE ANALYSIS
        # =====================================================

        st.subheader("📊 OI CHANGE ANALYSIS")

        total_call_change = option_df["CALL_CHG_OI"].sum()
        total_put_change = option_df["PUT_CHG_OI"].sum()

        cc1, cc2 = st.columns(2)

        cc1.metric(
            "CALL OI CHANGE",
            f"{int(total_call_change):,}"
        )

        cc2.metric(
            "PUT OI CHANGE",
            f"{int(total_put_change):,}"
        )

        # =====================================================
        # TABLE
        # =====================================================

        with st.expander("📂 VIEW FULL OPTION DATA"):

            st.dataframe(
                option_df,
                use_container_width=True
            )

    except Exception as e:

        st.error(f"🔴 OPTION CHAIN ERROR : {e}")

# =========================================================
# TAB 3 - AI SCANNER
# =========================================================

with tab3:

    st.header("🤖 MULTI STOCK AI SCANNER")

    scan_results = []

    progress = st.progress(0)

    total = len(nse_stocks)

    for idx, (name, symbol) in enumerate(nse_stocks.items()):

        try:

            df = load_market_data(
                symbol,
                "15m",
                "5d"
            )

            if not df.empty:

                df = add_indicators(df)

                latest = df.iloc[-1]

                signal, score, confidence = ai_signal(latest)

                scan_results.append({

                    "STOCK": name,
                    "PRICE": round(float(latest["Close"]),2),
                    "RSI": round(float(latest["RSI"]),2),
                    "SIGNAL": signal,
                    "CONFIDENCE": confidence,
                    "SCORE": score

                })

        except:
            pass

        progress.progress((idx + 1) / total)

    scan_df = pd.DataFrame(scan_results)

    if not scan_df.empty:

        st.dataframe(
            scan_df.sort_values(
                by="CONFIDENCE",
                ascending=False
            ),
            use_container_width=True
        )

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "🚀 NSE AI PRO MAX V5.0 | Institutional Quant Trading Engine"
)
