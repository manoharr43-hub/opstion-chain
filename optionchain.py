import streamlit as st
import yfinance as yf
import pandas as pd

from indicators import add_indicators
from option_signals import generate_signal
from oi_analysis import calculate_pcr, max_pain
from greeks import estimate_greeks

# =========================
# NSE STOCK LIST
# =========================
stocks = [
    "RELIANCE",
    "HDFCBANK",
    "INFY",
    "TCS",
    "ICICIBANK",
    "SBIN",
    "LT",
    "ITC",
    "AXISBANK"
]

# =========================
# MAIN DASHBOARD
# =========================
def option_chain_dashboard():

    st.sidebar.header("⚙️ Scanner Settings")

    stock = st.sidebar.selectbox("Select Stock", stocks)

    interval = st.sidebar.selectbox(
        "Interval",
        ["5m", "15m", "30m", "1h", "1d"]
    )

    period = st.sidebar.selectbox(
        "Period",
        ["5d", "1mo", "3mo"]
    )

    # =========================
    # STOCK DATA
    # =========================
    df = yf.download(
        stock + ".NS",
        period=period,
        interval=interval,
        progress=False
    )

    if df.empty:
        st.error("No data found")
        return

    # =========================
    # INDICATORS
    # =========================
    df = add_indicators(df)

    latest = df.iloc[-1]

    # =========================
    # OPTION CHAIN
    # =========================
    ticker = yf.Ticker(stock + ".NS")

    expiries = ticker.options

    if len(expiries) == 0:
        st.warning("No option chain available")
        return

    expiry = st.selectbox(
        "Select Expiry",
        expiries
    )

    opt = ticker.option_chain(expiry)

    calls = opt.calls
    puts = opt.puts

    # =========================
    # OI ANALYSIS
    # =========================
    pcr = calculate_pcr(calls, puts)

    mp = max_pain(calls, puts)

    # =========================
    # SIGNAL
    # =========================
    signal = generate_signal(latest)

    # =========================
    # GREEKS
    # =========================
    greeks = estimate_greeks()

    # =========================
    # METRICS
    # =========================
    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Close", round(latest['Close'], 2))
    col2.metric("RSI", round(latest['RSI'], 2))
    col3.metric("PCR", round(pcr, 2))
    col4.metric("Max Pain", mp)
    col5.metric("Signal", signal)

    # =========================
    # CHART
    # =========================
    st.subheader("📈 Price Chart")

    st.line_chart(
        df[['Close', 'EMA20', 'EMA50', 'VWAP']]
    )

    # =========================
    # OPTION CHAIN
    # =========================
    st.subheader("📊 CALL OPTION DATA")

    st.dataframe(
        calls[
            [
                'strike',
                'openInterest',
                'volume',
                'impliedVolatility'
            ]
        ]
    )

    st.subheader("📊 PUT OPTION DATA")

    st.dataframe(
        puts[
            [
                'strike',
                'openInterest',
                'volume',
                'impliedVolatility'
            ]
        ]
    )

    # =========================
    # GREEKS DISPLAY
    # =========================
    st.subheader("⚡ Greeks")

    st.write(greeks)
