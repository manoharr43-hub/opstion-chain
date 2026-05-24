# =========================================================
# 🚀 NSE AI PRO MAX V8.1 INSTITUTIONAL
# =========================================================

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go
import pytz
import io
import time
import urllib3

from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from streamlit_autorefresh import st_autorefresh

urllib3.disable_warnings()

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="NSE AI PRO MAX V8.1",
    page_icon="🚀",
    layout="wide"
)

# =========================================================
# AUTO REFRESH
# =========================================================

st_autorefresh(interval=60000, key="refresh")

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
    border-radius: 12px;
    padding: 15px;
    border: 1px solid #374151;
}

h1,h2,h3,h4 {
    color: white !important;
}

div.stButton > button:first-child {
    background-color: #2563EB;
    color: white;
    border-radius: 10px;
    width: 100%;
    border: none;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# TITLE
# =========================================================

st.title("🚀 NSE AI PRO MAX V8.1")
st.caption("Institutional Quantitative Trading Dashboard")

# =========================================================
# NSE STOCKS
# =========================================================

nse_stocks = {

    "NIFTY 50": "^NSEI",
    "BANKNIFTY": "^NSEBANK",

    "RELIANCE": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "INFY": "INFY.NS",
    "HDFCBANK": "HDFCBANK.NS",
    "ICICIBANK": "ICICIBANK.NS",
    "SBIN": "SBIN.NS",
    "AXISBANK": "AXISBANK.NS",
    "ITC": "ITC.NS",
    "LT": "LT.NS",
    "BHARTIARTL": "BHARTIARTL.NS",
    "TATAMOTORS": "TATAMOTORS.NS",
    "MARUTI": "MARUTI.NS",
    "BAJFINANCE": "BAJFINANCE.NS",
    "HINDUNILVR": "HINDUNILVR.NS",
    "SUNPHARMA": "SUNPHARMA.NS",
    "WIPRO": "WIPRO.NS",
    "POWERGRID": "POWERGRID.NS",
    "NTPC": "NTPC.NS",
    "TATASTEEL": "TATASTEEL.NS"
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
    "TIMEFRAME",
    ["5m", "15m", "30m", "1h"]
)

period = st.sidebar.selectbox(
    "PERIOD",
    ["1d", "5d", "1mo"]
)

ticker = nse_stocks[selected_stock]

# =========================================================
# INDIA TIME
# =========================================================

india = pytz.timezone("Asia/Kolkata")

current_time = datetime.now(india)

st.sidebar.info(
    current_time.strftime(
        "🕒 %d-%m-%Y %H:%M:%S IST"
    )
)

# =========================================================
# MARKET STATUS
# =========================================================

if (
    current_time.hour >= 9
    and
    current_time.hour <= 15
):

    st.sidebar.success("🟢 MARKET OPEN")

else:

    st.sidebar.error("🔴 MARKET CLOSED")

# =========================================================
# DATA LOADER
# =========================================================

@st.cache_data(ttl=60)

def load_data(ticker, interval, period):

    df = yf.download(
        ticker,
        interval=interval,
        period=period,
        progress=False,
        auto_adjust=True,
        threads=True
    )

    if isinstance(df.columns, pd.MultiIndex):

        df.columns = df.columns.get_level_values(0)

    return df

# =========================================================
# ATR
# =========================================================

def calculate_atr(df, period=14):

    high_low = df["High"] - df["Low"]

    high_close = abs(
        df["High"] - df["Close"].shift()
    )

    low_close = abs(
        df["Low"] - df["Close"].shift()
    )

    tr = pd.concat([
        high_low,
        high_close,
        low_close
    ], axis=1).max(axis=1)

    atr = tr.rolling(period).mean()

    return atr

# =========================================================
# INDICATORS
# =========================================================

def indicators(df):

    df = df.copy()

    # EMA

    df["EMA20"] = (
        df["Close"]
        .ewm(span=20, adjust=False)
        .mean()
    )

    df["EMA50"] = (
        df["Close"]
        .ewm(span=50, adjust=False)
        .mean()
    )

    # RSI

    delta = df["Close"].diff()

    gain = delta.clip(lower=0)

    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()

    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / (avg_loss + 1e-10)

    df["RSI"] = (
        100 - (100 / (1 + rs))
    )

    # MACD

    ema12 = df["Close"].ewm(span=12).mean()

    ema26 = df["Close"].ewm(span=26).mean()

    df["MACD"] = ema12 - ema26

    df["MACD_SIGNAL"] = (
        df["MACD"]
        .ewm(span=9)
        .mean()
    )

    # VWAP

    df["VWAP"] = (
        (df["Close"] * df["Volume"]).cumsum()
        /
        (df["Volume"].cumsum() + 1e-10)
    )

    # ATR

    df["ATR"] = calculate_atr(df)

    # SMART MONEY

    df["VOL_AVG"] = (
        df["Volume"]
        .rolling(20)
        .mean()
    )

    df["SMART_MONEY"] = (
        df["Volume"]
        >
        df["VOL_AVG"] * 2
    )

    df.fillna(0, inplace=True)

    return df

# =========================================================
# AI SIGNAL ENGINE
# =========================================================

def ai_signal(latest):

    score = 0

    if latest["EMA20"] > latest["EMA50"]:
        score += 25
    else:
        score -= 25

    if 55 <= latest["RSI"] <= 70:
        score += 20

    elif latest["RSI"] < 30:
        score += 15

    elif latest["RSI"] > 75:
        score -= 15

    if latest["MACD"] > latest["MACD_SIGNAL"]:
        score += 25
    else:
        score -= 25

    if latest["Close"] > latest["VWAP"]:
        score += 20
    else:
        score -= 20

    if latest["SMART_MONEY"]:
        score += 10

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
# OPTION CHAIN
# =========================================================

@st.cache_data(ttl=60)

def option_chain(symbol="NIFTY"):

    try:

        url = (
            f"https://www.nseindia.com/api/"
            f"option-chain-indices?symbol={symbol}"
        )

        headers = {

            "user-agent":
            "Mozilla/5.0",

            "accept-language":
            "en-US,en;q=0.9",

            "accept-encoding":
            "gzip, deflate, br"
        }

        session = requests.Session()

        session.get(
            "https://www.nseindia.com",
            headers=headers,
            timeout=10,
            verify=False
        )

        time.sleep(2)

        response = session.get(
            url,
            headers=headers,
            timeout=10,
            verify=False
        )

        if response.status_code != 200:

            st.error(
                f"NSE API ERROR : "
                f"{response.status_code}"
            )

            return pd.DataFrame()

        json_data = response.json()

        records = (
            json_data
            .get("records", {})
            .get("data", [])
        )

        rows = []

        for item in records:

            strike = item.get(
                "strikePrice", 0
            )

            ce = item.get("CE", {})
            pe = item.get("PE", {})

            rows.append({

                "STRIKE": strike,

                "CALL_OI":
                ce.get(
                    "openInterest", 0
                ),

                "PUT_OI":
                pe.get(
                    "openInterest", 0
                ),

                "CALL_CHG_OI":
                ce.get(
                    "changeinOpenInterest", 0
                ),

                "PUT_CHG_OI":
                pe.get(
                    "changeinOpenInterest", 0
                ),

                "CALL_LTP":
                ce.get(
                    "lastPrice", 0
                ),

                "PUT_LTP":
                pe.get(
                    "lastPrice", 0
                )
            })

        return pd.DataFrame(rows)

    except Exception as e:

        st.error(
            f"OPTION ERROR : {e}"
        )

        return pd.DataFrame()

# =========================================================
# TABS
# =========================================================

tab1, tab2, tab3 = st.tabs([
    "📈 TECHNICAL",
    "📂 OPTION CHAIN",
    "🤖 AI SCANNER"
])

# =========================================================
# TECHNICAL
# =========================================================

with tab1:

    try:

        df = load_data(
            ticker,
            interval,
            period
        )

        if df.empty:

            st.error("NO MARKET DATA")

            st.stop()

        df = indicators(df)

        latest = df.iloc[-1]

        signal, score, confidence = ai_signal(
            latest
        )

        st.subheader("🤖 AI SIGNAL")

        if "BUY" in signal:

            st.success(
                f"{signal} | "
                f"CONFIDENCE : {confidence}%"
            )

        elif "SELL" in signal:

            st.error(
                f"{signal} | "
                f"CONFIDENCE : {confidence}%"
            )

        else:

            st.warning(signal)

        # METRICS

        c1, c2, c3, c4, c5, c6 = st.columns(6)

        c1.metric(
            "PRICE",
            round(float(latest["Close"]),2)
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
            "ATR",
            round(float(latest["ATR"]),2)
        )

        c5.metric(
            "MACD",
            round(float(latest["MACD"]),2)
        )

        c6.metric(
            "AI SCORE",
            score
        )

        # STOPLOSS TARGET

        stoploss = (
            latest["Close"]
            -
            latest["ATR"] * 1.5
        )

        target = (
            latest["Close"]
            +
            latest["ATR"] * 3
        )

        s1, s2 = st.columns(2)

        s1.success(
            f"🛑 SL : "
            f"{round(float(stoploss),2)}"
        )

        s2.success(
            f"🎯 TARGET : "
            f"{round(float(target),2)}"
        )

        # CHART

        fig = go.Figure()

        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="PRICE"
        ))

        fig.add_trace(go.Scatter(
            x=df.index,
            y=df["EMA20"],
            mode="lines",
            name="EMA20"
        ))

        fig.add_trace(go.Scatter(
            x=df.index,
            y=df["EMA50"],
            mode="lines",
            name="EMA50"
        ))

        fig.update_layout(
            template="plotly_dark",
            height=700,
            xaxis_rangeslider_visible=False
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # SMART MONEY

        st.subheader("🏦 SMART MONEY")

        if latest["SMART_MONEY"]:

            st.success(
                "🔥 INSTITUTIONAL BUYING"
            )

        else:

            st.info(
                "Normal Market Flow"
            )

    except Exception as e:

        st.error(str(e))

# =========================================================
# OPTION CHAIN
# =========================================================

with tab2:

    st.header("📂 LIVE OPTION CHAIN")

    option_symbol = st.selectbox(
        "INDEX",
        ["NIFTY", "BANKNIFTY"]
    )

    option_df = option_chain(option_symbol)

    if not option_df.empty:

        total_call = option_df["CALL_OI"].sum()

        total_put = option_df["PUT_OI"].sum()

        pcr = (
            total_put / total_call
            if total_call > 0
            else 0
        )

        support = option_df.loc[
            option_df["PUT_OI"].idxmax(),
            "STRIKE"
        ]

        resistance = option_df.loc[
            option_df["CALL_OI"].idxmax(),
            "STRIKE"
        ]

        option_df["TOTAL_OI"] = (
            option_df["CALL_OI"]
            +
            option_df["PUT_OI"]
        )

        max_pain = option_df.loc[
            option_df["TOTAL_OI"].idxmax(),
            "STRIKE"
        ]

        m1, m2, m3, m4 = st.columns(4)

        m1.metric("PCR", round(pcr,2))
        m2.metric("SUPPORT", int(support))
        m3.metric("RESISTANCE", int(resistance))
        m4.metric("MAX PAIN", int(max_pain))

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
            height=700
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

        st.dataframe(
            option_df,
            use_container_width=True
        )

# =========================================================
# AI SCANNER
# =========================================================

with tab3:

    st.header("🤖 NSE AI SCANNER")

    results = []

    progress = st.progress(0)

    total = len(nse_stocks)

    def process_stock(item):

        name, symbol = item

        try:

            df = load_data(
                symbol,
                "15m",
                "5d"
            )

            if df.empty:
                return None

            df = indicators(df)

            latest = df.iloc[-1]

            signal, score, confidence = ai_signal(
                latest
            )

            return {

                "STOCK": name,

                "PRICE":
                round(
                    float(latest["Close"]),2
                ),

                "RSI":
                round(
                    float(latest["RSI"]),2
                ),

                "SIGNAL": signal,

                "CONFIDENCE": confidence,

                "SCORE": score
            }

        except:
            return None

    with ThreadPoolExecutor(
        max_workers=10
    ) as executor:

        for idx, result in enumerate(

            executor.map(
                process_stock,
                nse_stocks.items()
            )
        ):

            if result:

                results.append(result)

            progress.progress(
                (idx + 1) / total
            )

    scan_df = pd.DataFrame(results)

    if not scan_df.empty:

        scan_df = scan_df.sort_values(
            by="CONFIDENCE",
            ascending=False
        )

        st.dataframe(
            scan_df,
            use_container_width=True
        )

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "🚀 NSE AI PRO MAX V8.1 INSTITUTIONAL"
)
