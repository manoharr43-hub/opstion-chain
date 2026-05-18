# =========================================================
# 🚀 NSE AI PRO MAX V2 - MULTI STOCK SCANNER
# OLD CODE DISTURB KAKUNDA NEW VERSION
# =========================================================

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from concurrent.futures import ThreadPoolExecutor

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="NSE AI PRO MAX V2",
    layout="wide"
)

st.title("🚀 NSE AI PRO MAX V2")
st.caption("AI BASED MULTI STOCK NSE SCANNER")

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
    "BHARTIARTL": "BHARTIARTL.NS",
    "ASIANPAINT": "ASIANPAINT.NS",
    "AXISBANK": "AXISBANK.NS",
    "BAJFINANCE": "BAJFINANCE.NS",
    "HCLTECH": "HCLTECH.NS",
    "MARUTI": "MARUTI.NS",
    "SUNPHARMA": "SUNPHARMA.NS",
    "TATAMOTORS": "TATAMOTORS.NS",
    "WIPRO": "WIPRO.NS",
    "ULTRACEMCO": "ULTRACEMCO.NS",
    "POWERGRID": "POWERGRID.NS",
    "NTPC": "NTPC.NS",
    "ONGC": "ONGC.NS",
    "ADANIENT": "ADANIENT.NS",
    "ADANIPORTS": "ADANIPORTS.NS",
    "COALINDIA": "COALINDIA.NS",
    "HINDUNILVR": "HINDUNILVR.NS",
    "KOTAKBANK": "KOTAKBANK.NS",
    "BAJAJFINSV": "BAJAJFINSV.NS",
    "NESTLEIND": "NESTLEIND.NS",
    "TECHM": "TECHM.NS",
    "TITAN": "TITAN.NS"
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

    if df.empty:
        return df

    # FIX MULTI INDEX
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.reset_index()

    # EMA
    df['EMA20'] = df['Close'].ewm(span=20).mean()
    df['EMA50'] = df['Close'].ewm(span=50).mean()

    # VWAP
    df['VWAP'] = (
        (df['Close'] * df['Volume']).cumsum()
        / df['Volume'].cumsum()
    )

    # RSI
    delta = df['Close'].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss

    df['RSI'] = 100 - (100 / (1 + rs))
    df['RSI'] = df['RSI'].fillna(50)

    # ATR
    df['H-L'] = df['High'] - df['Low']
    df['H-PC'] = abs(df['High'] - df['Close'].shift(1))
    df['L-PC'] = abs(df['Low'] - df['Close'].shift(1))

    df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)

    df['ATR'] = df['TR'].rolling(14).mean()

    # MACD
    exp1 = df['Close'].ewm(span=12).mean()
    exp2 = df['Close'].ewm(span=26).mean()

    df['MACD'] = exp1 - exp2
    df['MACD_SIGNAL'] = df['MACD'].ewm(span=9).mean()

    # VOLUME BREAKOUT
    df['VOL_AVG'] = df['Volume'].rolling(20).mean()

    df['VOL_BREAKOUT'] = (
        df['Volume'] > df['VOL_AVG'] * 1.5
    )

    return df

# =========================================================
# SIGNAL FUNCTION
# =========================================================

def generate_signal(df):

    latest = df.iloc[-1]

    score = 0

    # EMA
    if latest['EMA20'] > latest['EMA50']:
        score += 25

    # VWAP
    if latest['Close'] > latest['VWAP']:
        score += 25

    # RSI
    if 55 < latest['RSI'] < 70:
        score += 25

    # MACD
    if latest['MACD'] > latest['MACD_SIGNAL']:
        score += 25

    # FINAL SIGNAL

    if score >= 75:
        signal = "🚀 STRONG BUY"

    elif score >= 50:
        signal = "✅ BUY"

    elif score >= 25:
        signal = "⚠️ SIDEWAYS"

    else:
        signal = "🔻 SELL"

    return signal, score

# =========================================================
# SINGLE STOCK DATA
# =========================================================

try:

    df = yf.download(
        ticker,
        interval=interval,
        period=period,
        progress=False,
        auto_adjust=True
    )

    if df.empty:
        st.error("NO DATA FOUND")
        st.stop()

    df = calculate_indicators(df)

    signal, score = generate_signal(df)

    latest = df.iloc[-1]

    # =====================================================
    # SIGNAL DISPLAY
    # =====================================================

    st.subheader("🤖 AI SIGNAL")

    if "STRONG BUY" in signal:
        st.success(signal)

    elif "BUY" in signal:
        st.info(signal)

    elif "SELL" in signal:
        st.error(signal)

    else:
        st.warning(signal)

    # =====================================================
    # LIVE METRICS
    # =====================================================

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "PRICE",
        f"₹ {round(latest['Close'], 2)}"
    )

    col2.metric(
        "RSI",
        round(latest['RSI'], 2)
    )

    col3.metric(
        "VWAP",
        round(latest['VWAP'], 2)
    )

    col4.metric(
        "ATR",
        round(latest['ATR'], 2)
    )

    col5.metric(
        "AI SCORE",
        score
    )

    # =====================================================
    # CHART
    # =====================================================

    st.subheader(f"📈 {selected_stock} LIVE CHART")

    fig = go.Figure()

    # TIME COLUMN FIX
    time_col = df.columns[0]

    fig.add_trace(go.Scatter(
        x=df[time_col],
        y=df['Close'],
        mode='lines',
        name='Close'
    ))

    fig.add_trace(go.Scatter(
        x=df[time_col],
        y=df['EMA20'],
        mode='lines',
        name='EMA20'
    ))

    fig.add_trace(go.Scatter(
        x=df[time_col],
        y=df['EMA50'],
        mode='lines',
        name='EMA50'
    ))

    fig.add_trace(go.Scatter(
        x=df[time_col],
        y=df['VWAP'],
        mode='lines',
        name='VWAP'
    ))

    fig.update_layout(
        height=650,
        hovermode="x unified",
        xaxis_title="TIME",
        yaxis_title="PRICE"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # =====================================================
    # DATA TABLE
    # =====================================================

    st.subheader("📊 LIVE MARKET DATA")

    show_df = df[[
        'Close',
        'EMA20',
        'EMA50',
        'VWAP',
        'RSI',
        'ATR',
        'MACD'
    ]].tail(20)

    st.dataframe(
        show_df,
        use_container_width=True
    )

    # =====================================================
    # RSI STATUS
    # =====================================================

    st.subheader("📈 RSI STATUS")

    rsi = latest['RSI']

    if rsi > 70:

        st.error(f"RSI {round(rsi,2)} → OVERBOUGHT")

    elif rsi < 30:

        st.success(f"RSI {round(rsi,2)} → OVERSOLD")

    else:

        st.info(f"RSI {round(rsi,2)} → NORMAL")

    # =====================================================
    # MULTI STOCK AI SCANNER
    # =====================================================

    st.subheader("🔥 LIVE AI STOCK SCANNER")

    def scan_stock(item):

        stock_name, stock_ticker = item

        try:

            data = yf.download(
                stock_ticker,
                interval=interval,
                period=period,
                progress=False,
                auto_adjust=True
            )

            if data.empty:
                return None

            data = calculate_indicators(data)

            signal, score = generate_signal(data)

            latest = data.iloc[-1]

            return {
                "STOCK": stock_name,
                "PRICE": round(latest['Close'], 2),
                "RSI": round(latest['RSI'], 2),
                "MACD": round(latest['MACD'], 2),
                "SIGNAL": signal,
                "SCORE": score
            }

        except:
            return None

    results = []

    # FAST SCANNER
    with ThreadPoolExecutor(max_workers=10) as executor:

        scanned = executor.map(
            scan_stock,
            nse_stocks.items()
        )

    for item in scanned:

        if item is not None:
            results.append(item)

    scanner_df = pd.DataFrame(results)

    # SORT BY SCORE
    scanner_df = scanner_df.sort_values(
        by="SCORE",
        ascending=False
    )

    st.dataframe(
        scanner_df,
        use_container_width=True
    )

    # =====================================================
    # TOP BUY STOCKS
    # =====================================================

    st.subheader("🚀 TOP BUY STOCKS")

    top_buy = scanner_df[
        scanner_df['SIGNAL'].str.contains("BUY")
    ]

    st.dataframe(
        top_buy.head(10),
        use_container_width=True
    )

    # =====================================================
    # TOP SELL STOCKS
    # =====================================================

    st.subheader("🔻 TOP SELL STOCKS")

    top_sell = scanner_df[
        scanner_df['SIGNAL'].str.contains("SELL")
    ]

    st.dataframe(
        top_sell.head(10),
        use_container_width=True
    )

except Exception as e:

    st.error("APP ERROR")

    st.code(str(e))
