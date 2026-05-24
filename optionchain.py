# =========================================================
# 🚀 NSE AI PRO MAX V8.0 ELITE
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

from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from streamlit_autorefresh import st_autorefresh

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="NSE AI PRO MAX V8.0 ELITE",
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
    border: 1px solid #374151;
    border-radius: 12px;
    padding: 15px;
}

h1,h2,h3,h4 {
    color: white !important;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# TITLE
# =========================================================

st.title("🚀 NSE AI PRO MAX V8.0 ELITE")
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

    high_close = np.abs(
        df["High"] - df["Close"].shift()
    )

    low_close = np.abs(
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

    df["RSI"] = 100 - (
        100 / (1 + rs)
    )

    # MACD

    ema12 = df["Close"].ewm(span=12).mean()

    ema26 = df["Close"].ewm(span=26).mean()

    df["MACD"] = ema12 - ema26

    df["MACD_SIGNAL"] = (
        df["MACD"].ewm(span=9).mean()
    )

    # VWAP

    df["VWAP"] = (
        (df["Close"] * df["Volume"]).cumsum()
        /
        (df["Volume"].cumsum() + 1e-10)
    )

    # ATR

    df["ATR"] = calculate_atr(df)

    # VOLUME

    df["VOL_AVG"] = (
        df["Volume"].rolling(20).mean()
    )

    df["SMART_MONEY"] = (
        df["Volume"] > df["VOL_AVG"] * 2
    )

    df.fillna(0, inplace=True)

    return df

# =========================================================
# AI ENGINE
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

    # SMART MONEY

    if latest["SMART_MONEY"]:
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
            "user-agent": "Mozilla/5.0"
        }

        session = requests.Session()

        session.get(
            "https://www.nseindia.com",
            headers=headers,
            timeout=10
        )

        response = session.get(
            url,
            headers=headers,
            timeout=10
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

                "CALL_OI":
                ce.get("openInterest", 0),

                "PUT_OI":
                pe.get("openInterest", 0),

                "CALL_CHG":
                ce.get(
                    "changeinOpenInterest", 0
                ),

                "PUT_CHG":
                pe.get(
                    "changeinOpenInterest", 0
                )
            })

        return pd.DataFrame(rows)

    except:

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
# TECHNICAL TAB
# =========================================================

with tab1:

    try:

        df = load_data(
            ticker,
            interval,
            period
        )

        if df.empty:

            st.error("NO DATA")

            st.stop()

        df = indicators(df)

        latest = df.iloc[-1]

        signal, score, confidence = ai_signal(
            latest
        )

        signal_time = datetime.now(
            india
        ).strftime(
            "%d-%m-%Y %H:%M:%S"
        )

        # SIGNAL

        st.subheader("🤖 AI SIGNAL")

        st.success(
            f"{signal} | "
            f"CONFIDENCE : {confidence}%"
        )

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

        # ATR SL TARGET

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
            f"🛑 STOPLOSS : "
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
                "🔥 INSTITUTIONAL ACTIVITY"
            )

        else:

            st.info(
                "Normal Market Flow"
            )

        # DOWNLOAD

        export_df = pd.DataFrame([{

            "TIME": signal_time,
            "STOCK": selected_stock,
            "PRICE": latest["Close"],
            "RSI": latest["RSI"],
            "VWAP": latest["VWAP"],
            "ATR": latest["ATR"],
            "SIGNAL": signal,
            "CONFIDENCE": confidence

        }])

        excel = io.BytesIO()

        with pd.ExcelWriter(
            excel,
            engine="openpyxl"
        ) as writer:

            export_df.to_excel(
                writer,
                index=False
            )

        st.download_button(

            "📥 DOWNLOAD SIGNAL",

            data=excel.getvalue(),

            file_name=
            f"{selected_stock}_SIGNAL.xlsx"
        )

    except Exception as e:

        st.error(str(e))

# =========================================================
# OPTION CHAIN TAB
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

        # OI CHART

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

# =========================================================
# AI SCANNER
# =========================================================

with tab3:

    st.header("🤖 AI SCANNER")

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

                "CONFIDENCE":
                confidence,

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

        # DOWNLOAD

        scan_excel = io.BytesIO()

        with pd.ExcelWriter(
            scan_excel,
            engine="openpyxl"
        ) as writer:

            scan_df.to_excel(
                writer,
                index=False
            )

        st.download_button(

            "📥 DOWNLOAD AI SCANNER",

            data=scan_excel.getvalue(),

            file_name="AI_SCANNER.xlsx"
        )

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "🚀 NSE AI PRO MAX V8.0 ELITE"
)
