# =========================================================
# 🚀 NSE AI PRO MAX V7.0 SUPREME
# =========================================================
# LIVE NSE AI ENGINE
# SIGNAL TIME SYSTEM
# EXCEL DOWNLOAD
# LIVE OPTION CHAIN
# MAX PAIN ANALYSIS
# SMART MONEY FLOW
# AI STOCK SCANNER
# INSTITUTIONAL DASHBOARD
# =========================================================

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go
import pytz
import io

from datetime import datetime

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="NSE AI PRO MAX V7.0 SUPREME",
    page_icon="🚀",
    layout="wide"
)

# =========================================================
# DARK THEME
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

st.title("🚀 NSE AI PRO MAX V7.0 SUPREME")
st.caption("Institutional AI Quantitative Trading System")

# =========================================================
# NSE STOCK DATABASE
# =========================================================

nse_stocks = {

    # INDEX

    "NIFTY 50": "^NSEI",
    "BANKNIFTY": "^NSEBANK",

    # BANKS

    "HDFCBANK": "HDFCBANK.NS",
    "ICICIBANK": "ICICIBANK.NS",
    "SBIN": "SBIN.NS",
    "AXISBANK": "AXISBANK.NS",
    "KOTAKBANK": "KOTAKBANK.NS",
    "PNB": "PNB.NS",
    "BANKBARODA": "BANKBARODA.NS",
    "FEDERALBNK": "FEDERALBNK.NS",
    "IDFCFIRSTB": "IDFCFIRSTB.NS",

    # IT

    "TCS": "TCS.NS",
    "INFY": "INFY.NS",
    "WIPRO": "WIPRO.NS",
    "HCLTECH": "HCLTECH.NS",
    "TECHM": "TECHM.NS",
    "LTIM": "LTIM.NS",

    # AUTO

    "MARUTI": "MARUTI.NS",
    "TATAMOTORS": "TATAMOTORS.NS",
    "M&M": "M&M.NS",
    "BAJAJ-AUTO": "BAJAJ-AUTO.NS",
    "HEROMOTOCO": "HEROMOTOCO.NS",

    # PHARMA

    "SUNPHARMA": "SUNPHARMA.NS",
    "DRREDDY": "DRREDDY.NS",
    "CIPLA": "CIPLA.NS",
    "DIVISLAB": "DIVISLAB.NS",

    # FMCG

    "ITC": "ITC.NS",
    "HINDUNILVR": "HINDUNILVR.NS",
    "NESTLEIND": "NESTLEIND.NS",

    # ENERGY

    "RELIANCE": "RELIANCE.NS",
    "ONGC": "ONGC.NS",
    "IOC": "IOC.NS",
    "NTPC": "NTPC.NS",
    "POWERGRID": "POWERGRID.NS",

    # METALS

    "TATASTEEL": "TATASTEEL.NS",
    "JSWSTEEL": "JSWSTEEL.NS",
    "HINDALCO": "HINDALCO.NS",

    # TELECOM

    "BHARTIARTL": "BHARTIARTL.NS",

    # OTHERS

    "LT": "LT.NS",
    "BAJFINANCE": "BAJFINANCE.NS",
    "BAJAJFINSV": "BAJAJFINSV.NS",
    "TITAN": "TITAN.NS",
    "ASIANPAINT": "ASIANPAINT.NS",
    "IRCTC": "IRCTC.NS",
    "ZOMATO": "ZOMATO.NS"
}

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("⚙️ AI CONTROL PANEL")

selected_stock = st.sidebar.selectbox(
    "SELECT NSE STOCK",
    sorted(list(nse_stocks.keys()))
)

interval = st.sidebar.selectbox(
    "SELECT TIMEFRAME",
    ["5m", "15m", "30m", "1h"]
)

period = st.sidebar.selectbox(
    "SELECT PERIOD",
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

if 9 <= current_time.hour <= 15:

    st.sidebar.success("🟢 MARKET OPEN")

else:

    st.sidebar.error("🔴 MARKET CLOSED")

# =========================================================
# CACHE DATA
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

def calculate_indicators(df):

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

    # SMART MONEY

    df["VOL_AVG"] = df["Volume"].rolling(20).mean()

    df["SMART_MONEY"] = (
        df["Volume"] > df["VOL_AVG"] * 2
    )

    df.fillna(0, inplace=True)

    return df

# =========================================================
# AI SIGNAL ENGINE
# =========================================================

def generate_signal(latest):

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

    confidence = min(abs(score), 95)

    return signal, score, confidence

# =========================================================
# OPTION CHAIN API
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

            "CALL_OI": ce.get(
                "openInterest", 0
            ),

            "PUT_OI": pe.get(
                "openInterest", 0
            ),

            "CALL_CHG_OI": ce.get(
                "changeinOpenInterest", 0
            ),

            "PUT_CHG_OI": pe.get(
                "changeinOpenInterest", 0
            )
        })

    return pd.DataFrame(rows)

# =========================================================
# TABS
# =========================================================

tab1, tab2, tab3 = st.tabs([
    "📈 LIVE TECHNICAL",
    "📂 OPTION CHAIN",
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

        data = calculate_indicators(data)

        latest = data.iloc[-1]

        signal, score, confidence = generate_signal(latest)

        signal_time = datetime.now(india).strftime(
            "%d-%m-%Y %H:%M:%S"
        )

        # =====================================================
        # SIGNAL DISPLAY
        # =====================================================

        st.subheader("🤖 AI SIGNAL ENGINE")

        if "BUY" in signal:

            st.success(
                f"""
                {signal}
                
                🎯 CONFIDENCE : {confidence}%
                
                ⏰ SIGNAL TIME : {signal_time} IST
                """
            )

        elif "SELL" in signal:

            st.error(
                f"""
                {signal}
                
                🎯 CONFIDENCE : {confidence}%
                
                ⏰ SIGNAL TIME : {signal_time} IST
                """
            )

        else:

            st.warning(
                f"""
                {signal}
                
                🎯 CONFIDENCE : {confidence}%
                
                ⏰ SIGNAL TIME : {signal_time} IST
                """
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
        # CHART
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
        # SMART MONEY
        # =====================================================

        st.subheader("🏦 SMART MONEY FLOW")

        if latest["SMART_MONEY"]:

            st.success(
                "🔥 INSTITUTIONAL BUYING DETECTED"
            )

        else:

            st.info(
                "Normal Trading Activity"
            )

        # =====================================================
        # EXCEL DOWNLOAD
        # =====================================================

        signal_df = pd.DataFrame([{

            "TIME": signal_time,

            "STOCK": selected_stock,

            "PRICE": round(
                float(latest["Close"]),2
            ),

            "RSI": round(
                float(latest["RSI"]),2
            ),

            "VWAP": round(
                float(latest["VWAP"]),2
            ),

            "MACD": round(
                float(latest["MACD"]),2
            ),

            "SIGNAL": signal,

            "CONFIDENCE": confidence,

            "AI_SCORE": score
        }])

        excel_buffer = io.BytesIO()

        with pd.ExcelWriter(
            excel_buffer,
            engine="openpyxl"
        ) as writer:

            signal_df.to_excel(
                writer,
                index=False,
                sheet_name="AI_SIGNAL"
            )

        excel_data = excel_buffer.getvalue()

        st.download_button(

            label="📥 DOWNLOAD SIGNAL EXCEL",

            data=excel_data,

            file_name=f"{selected_stock}_AI_SIGNAL.xlsx",

            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # =====================================================
        # SIGNAL DATA
        # =====================================================

        with st.expander("📂 VIEW SIGNAL DATA"):

            st.dataframe(
                signal_df,
                use_container_width=True
            )

    except Exception as e:

        st.error(f"🔴 ERROR : {e}")

# =========================================================
# TAB 2 - OPTION CHAIN
# =========================================================

with tab2:

    st.header("📂 LIVE NSE OPTION CHAIN")

    option_symbol = st.selectbox(
        "SELECT INDEX",
        ["NIFTY", "BANKNIFTY"]
    )

    try:

        option_df = get_option_chain(option_symbol)

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

        # =====================================================
        # SIGNAL
        # =====================================================

        if pcr > 1.15:

            st.success("🚀 BULLISH")

        elif pcr < 0.85:

            st.error("🔻 BEARISH")

        else:

            st.warning("⚠️ SIDEWAYS")

        # =====================================================
        # METRICS
        # =====================================================

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
            title="LIVE OI ANALYSIS"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

        # =====================================================
        # DOWNLOAD OPTION DATA
        # =====================================================

        option_excel = io.BytesIO()

        with pd.ExcelWriter(
            option_excel,
            engine="openpyxl"
        ) as writer:

            option_df.to_excel(
                writer,
                index=False,
                sheet_name="OPTION_CHAIN"
            )

        option_data = option_excel.getvalue()

        st.download_button(

            label="📥 DOWNLOAD OPTION CHAIN EXCEL",

            data=option_data,

            file_name=f"{option_symbol}_OPTION_CHAIN.xlsx",

            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:

        st.error(f"🔴 OPTION ERROR : {e}")

# =========================================================
# TAB 3 - AI SCANNER
# =========================================================

with tab3:

    st.header("🤖 NSE AI SCANNER")

    results = []

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

                df = calculate_indicators(df)

                latest = df.iloc[-1]

                signal, score, confidence = generate_signal(latest)

                results.append({

                    "STOCK": name,

                    "PRICE": round(
                        float(latest["Close"]),2
                    ),

                    "RSI": round(
                        float(latest["RSI"]),2
                    ),

                    "SIGNAL": signal,

                    "CONFIDENCE": confidence,

                    "SCORE": score
                })

        except:
            pass

        progress.progress(
            (idx + 1) / total
        )

    scan_df = pd.DataFrame(results)

    if not scan_df.empty:

        st.dataframe(
            scan_df.sort_values(
                by="CONFIDENCE",
                ascending=False
            ),
            use_container_width=True
        )

        # =====================================================
        # SCANNER DOWNLOAD
        # =====================================================

        scan_excel = io.BytesIO()

        with pd.ExcelWriter(
            scan_excel,
            engine="openpyxl"
        ) as writer:

            scan_df.to_excel(
                writer,
                index=False,
                sheet_name="AI_SCANNER"
            )

        scan_data = scan_excel.getvalue()

        st.download_button(

            label="📥 DOWNLOAD AI SCANNER EXCEL",

            data=scan_data,

            file_name="NSE_AI_SCANNER.xlsx",

            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "🚀 NSE AI PRO MAX V7.0 SUPREME | Institutional Quantitative Trading System"
)
