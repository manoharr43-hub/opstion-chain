# =========================================================
# 🚀 NSE AI PRO MAX V2.1 - MULTI STOCK SCANNER (UPGRADED)
# OLD LOGIC PRESERVED - NEW ADVANCED FEATURES ADDED
# =========================================================

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from concurrent.futures import ThreadPoolExecutor

# =========================================================
# PAGE CONFIG & AUTO REFRESH (60 SECONDS)
# =========================================================

st.set_page_config(
    page_title="NSE AI PRO MAX V2.1",
    layout="wide"
)

# AUTO REFRESH RUNS EVERY 60,000 MILLISECONDS (1 MINUTE)
st.fragment(run_every=60)

st.title("🚀 NSE AI PRO MAX V2.1")
st.caption("ADVANCED AI BASED MULTI STOCK NSE SCANNER WITH SCORE LOGIC")

# =========================================================
# FULL NIFTY 50 STOCK LIST
# =========================================================

nse_stocks = {
    "ADANIENT": "ADANIENT.NS", "ADANIPORTS": "ADANIPORTS.NS", "APOLLOHOSP": "APOLLOHOSP.NS",
    "ASIANPAINT": "ASIANPAINT.NS", "AXISBANK": "AXISBANK.NS", "BAJAJ-AUTO": "BAJAJ-AUTO.NS",
    "BAJAJFINSV": "BAJAJFINSV.NS", "BAJFINANCE": "BAJFINANCE.NS", "BEL": "BEL.NS",
    "BHARTIARTL": "BHARTIARTL.NS", "BPCL": "BPCL.NS", "BRITANNIA": "BRITANNIA.NS",
    "CIPLA": "CIPLA.NS", "COALINDIA": "COALINDIA.NS", "DIVISLAB": "DIVISLAB.NS",
    "DRREDDY": "DRREDDY.NS", "EICHERMOT": "EICHERMOT.NS", "GRASIM": "GRASIM.NS",
    "HCLTECH": "HCLTECH.NS", "HDFCBANK": "HDFCBANK.NS", "HDFCLIFE": "HDFCLIFE.NS",
    "HEROMOTOCO": "HEROMOTOCO.NS", "HINDALCO": "HINDALCO.NS", "HINDUNILVR": "HINDUNILVR.NS",
    "ICICIBANK": "ICICIBANK.NS", "INDUSINDBK": "INDUSINDBK.NS", "INFY": "INFY.NS",
    "ITC": "ITC.NS", "JSWSTEEL": "JSWSTEEL.NS", "KOTAKBANK": "KOTAKBANK.NS",
    "LT": "LT.NS", "M&M": "M&M.NS", "MARUTI": "MARUTI.NS", "NESTLEIND": "NESTLEIND.NS",
    "NTPC": "NTPC.NS", "ONGC": "ONGC.NS", "POWERGRID": "POWERGRID.NS", "RELIANCE": "RELIANCE.NS",
    "SBILIFE": "SBILIFE.NS", "SBIN": "SBIN.NS", "SUNPHARMA": "SUNPHARMA.NS",
    "TATACONSUM": "TATACONSUM.NS", "TATAMOTORS": "TATAMOTORS.NS", "TATASTEEL": "TATASTEEL.NS",
    "TCS": "TCS.NS", "TECHM": "TECHM.NS", "TITAN": "TITAN.NS", "ULTRACEMCO": "ULTRACEMCO.NS",
    "WIPRO": "WIPRO.NS", "TRENT": "TRENT.NS"
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
# ADVANCED SIGNAL FUNCTION (+100 to -100 LOGIC)
# =========================================================

def generate_signal(df):

    latest = df.iloc[-1]

    score = 0

    # EMA
    if latest['EMA20'] > latest['EMA50']:
        score += 25
    else:
        score -= 25

    # VWAP
    if latest['Close'] > latest['VWAP']:
        score += 25
    else:
        score -= 25

    # RSI
    if 55 < latest['RSI'] < 70:
        score += 25
    elif latest['RSI'] > 70:
        score -= 10  # OVERBOUGHT DANGER
    elif latest['RSI'] < 30:
        score += 15  # OVERSOLD PULLBACK POTENTIAL
    else:
        score -= 10  # NO MOMENTUM

    # MACD
    if latest['MACD'] > latest['MACD_SIGNAL']:
        score += 25
    else:
        score -= 25

    # FINAL SIGNAL DIRECTION
    if score >= 75:
        signal = "🚀 STRONG BUY"
    elif score >= 25:
        signal = "✅ BUY"
    elif score <= -75:
        signal = "🚨 STRONG SELL"
    elif score <= -25:
        signal = "🔻 SELL"
    else:
        signal = "⚠️ SIDEWAYS"

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
        st.success(f"{signal} (SCORE: {score})")
    elif "BUY" in signal:
        st.info(f"{signal} (SCORE: {score})")
    elif "STRONG SELL" in signal or "SELL" in signal:
        st.error(f"{signal} (SCORE: {score})")
    else:
        st.warning(f"{signal} (SCORE: {score})")

    # =====================================================
    # LIVE METRICS
    # =====================================================

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("PRICE", f"₹ {round(latest['Close'], 2)}")
    col2.metric("RSI", round(latest['RSI'], 2))
    col3.metric("VWAP", round(latest['VWAP'], 2))
    col4.metric("ATR", round(latest['ATR'], 2))
    col5.metric("AI SCORE", f"{score} PTS")

    # =====================================================
    # CHART
    # =====================================================

    st.subheader(f"📈 {selected_stock} LIVE CHART")

    fig = go.Figure()

    time_col = df.columns[0]

    fig.add_trace(go.Scatter(x=df[time_col], y=df['Close'], mode='lines', name='Close'))
    fig.add_trace(go.Scatter(x=df[time_col], y=df['EMA20'], mode='lines', name='EMA20'))
    fig.add_trace(go.Scatter(x=df[time_col], y=df['EMA50'], mode='lines', name='EMA50'))
    fig.add_trace(go.Scatter(x=df[time_col], y=df['VWAP'], mode='lines', name='VWAP'))

    fig.update_layout(
        height=500,
        hovermode="x unified",
        xaxis_title="TIME",
        yaxis_title="PRICE"
    )

    st.plotly_chart(fig, use_container_width=True)

    # =====================================================
    # DATA TABLE
    # =====================================================

    st.subheader("📊 LIVE MARKET DATA")

    show_df = df[['Close', 'EMA20', 'EMA50', 'VWAP', 'RSI', 'ATR', 'MACD']].tail(20)
    st.dataframe(show_df, use_container_width=True)

    # =====================================================
    # RSI STATUS
    # =====================================================

    st.subheader("📈 RSI STATUS")
    rsi = latest['RSI']

    if rsi > 70:
        st.error(f"RSI {round(rsi,2)} → OVERBOUGHT (RISKY FOR FRESH BUY)")
    elif rsi < 30:
        st.success(f"RSI {round(rsi,2)} → OVERSOLD (REVERSAL ZONE)")
    else:
        st.info(f"RSI {round(rsi,2)} → NORMAL")

    # =====================================================
    # MULTI STOCK AI SCANNER
    # =====================================================

    st.subheader("🔥 LIVE AI NIFTY 50 SCANNER")

    def scan_stock(item):
        stock_name, stock_ticker = item
        try:
            data = yf.download(stock_ticker, interval=interval, period=period, progress=False, auto_adjust=True)
            if data.empty:
                return None

            data = calculate_indicators(data)
            signal, score = generate_signal(data)
            latest = data.iloc[-1]

            # CHECK VOLUME BREAKOUT VALUE
            vol_bo = "🔥 YES" if latest['VOL_BREAKOUT'] else "⚪ NO"

            return {
                "STOCK": stock_name,
                "PRICE": round(latest['Close'], 2),
                "RSI": round(latest['RSI'], 2),
                "MACD": round(latest['MACD'], 2),
                "VOL_BO": vol_bo,
                "SIGNAL": signal,
                "SCORE": score
            }
        except:
            return None

    results = []

    # FAST MULTI-THREADED SCANNING
    with ThreadPoolExecutor(max_workers=15) as executor:
        scanned = executor.map(scan_stock, nse_stocks.items())

    for item in scanned:
        if item is not None:
            results.append(item)

    scanner_df = pd.DataFrame(results)
    
    # SORT BY HIGHEST SCORE TO LOWEST SCORE
    scanner_df = scanner_df.sort_values(by="SCORE", ascending=False)

    st.dataframe(scanner_df, use_container_width=True, hide_index=True)

    # =====================================================
    # SEPARATED FILTERS (BUY / SELL STOCKS)
    # =====================================================

    col_buy, col_sell = st.columns(2)

    with col_buy:
        st.subheader("🚀 TOP BUY CANDIDATES")
        top_buy = scanner_df[scanner_df['SIGNAL'].str.contains("BUY")].head(10)
        st.dataframe(top_buy, use_container_width=True, hide_index=True)

    with col_sell:
        st.subheader("🔻 TOP SELL CANDIDATES")
        top_sell = scanner_df[scanner_df['SIGNAL'].str.contains("SELL")].head(10)
        st.dataframe(top_sell, use_container_width=True, hide_index=True)

except Exception as e:
    st.error("APP ERROR")
    st.code(str(e))
