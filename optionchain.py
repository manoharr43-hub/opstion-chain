# =========================================================
# 🚀 NSE AI PRO MAX - ALL NSE STOCKS SCANNER
# =========================================================

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="NSE AI PRO MAX",
    layout="wide"
)

st.title("🚀 NSE AI PRO MAX")
st.caption("AI BASED NSE STOCK SIGNAL SCANNER")

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
    "SELECT NSE STOCK",
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
# DOWNLOAD DATA
# =========================================================

try:

    df = yf.download(
        ticker,
        interval=interval,
        period=period,
        progress=False,
        auto_adjust=True
    )

    # =====================================================
    # EMPTY DATA FIX
    # =====================================================

    if df.empty:
        st.error("NO DATA FOUND")
        st.stop()

    # =====================================================
    # FIX MULTI INDEX
    # =====================================================

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # =====================================================
    # RESET INDEX
    # =====================================================

    df = df.reset_index()

    # =====================================================
    # INDICATORS
    # =====================================================

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

    # =====================================================
    # AI SIGNAL LOGIC
    # =====================================================

    df['BUY'] = (
        (df['EMA20'] > df['EMA50']) &
        (df['Close'] > df['VWAP']) &
        (df['RSI'] > 55)
    )

    df['SELL'] = (
        (df['EMA20'] < df['EMA50']) &
        (df['Close'] < df['VWAP']) &
        (df['RSI'] < 45)
    )

    latest = df.iloc[-1]

    # =====================================================
    # SIGNAL DISPLAY
    # =====================================================

    st.subheader("🤖 AI SIGNAL")

    if latest['BUY']:

        st.success("🚀 STRONG BUY SIGNAL DETECTED")

    elif latest['SELL']:

        st.error("🔻 STRONG SELL SIGNAL DETECTED")

    else:

        st.warning("⚠️ SIDEWAYS / WAIT")

    # =====================================================
    # LIVE METRICS
    # =====================================================

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "LIVE PRICE",
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

    # =====================================================
    # CHART
    # =====================================================

    st.subheader(f"📈 {selected_stock} LIVE CHART")

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['Close'],
        mode='lines',
        name='Close'
    ))

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['EMA20'],
        mode='lines',
        name='EMA20'
    ))

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['EMA50'],
        mode='lines',
        name='EMA50'
    ))

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['VWAP'],
        mode='lines',
        name='VWAP'
    ))

    fig.update_layout(
        height=650,
        xaxis_title="TIME",
        yaxis_title="PRICE",
        hovermode="x unified"
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
        'ATR'
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

except Exception as e:

    st.error("APP ERROR")

    st.code(str(e))
