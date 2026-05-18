# =========================================================
# 🚀 OPTION CHAIN ANALYZER - NSE AI PRO MAX
# =========================================================

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# =========================================================
# PAGE TITLE
# =========================================================

st.title("📊 NSE OPTION CHAIN ANALYZER")

# =========================================================
# STOCK LIST
# =========================================================

option_stocks = {
    "NIFTY": "^NSEI",
    "BANKNIFTY": "^NSEBANK",
    "RELIANCE": "RELIANCE.NS",
    "SBIN": "SBIN.NS",
    "TCS": "TCS.NS",
    "INFY": "INFY.NS"
}

# =========================================================
# SIDEBAR
# =========================================================

selected_stock = st.sidebar.selectbox(
    "SELECT SYMBOL",
    list(option_stocks.keys())
)

ticker_symbol = option_stocks[selected_stock]

# =========================================================
# GET TICKER
# =========================================================

ticker = yf.Ticker(ticker_symbol)

# =========================================================
# EXPIRY DATES
# =========================================================

expiry_dates = ticker.options

if len(expiry_dates) == 0:

    st.error("NO OPTION DATA AVAILABLE")
    st.stop()

selected_expiry = st.sidebar.selectbox(
    "SELECT EXPIRY",
    expiry_dates
)

# =========================================================
# OPTION CHAIN DATA
# =========================================================

option_chain = ticker.option_chain(selected_expiry)

calls = option_chain.calls
puts = option_chain.puts

# =========================================================
# CLEAN DATA
# =========================================================

call_df = calls[[
    'strike',
    'lastPrice',
    'volume',
    'openInterest',
    'impliedVolatility'
]]

put_df = puts[[
    'strike',
    'lastPrice',
    'volume',
    'openInterest',
    'impliedVolatility'
]]

# RENAME

call_df.columns = [
    'STRIKE',
    'CALL_LTP',
    'CALL_VOLUME',
    'CALL_OI',
    'CALL_IV'
]

put_df.columns = [
    'STRIKE',
    'PUT_LTP',
    'PUT_VOLUME',
    'PUT_OI',
    'PUT_IV'
]

# =========================================================
# MERGE DATA
# =========================================================

merged_df = pd.merge(
    call_df,
    put_df,
    on='STRIKE'
)

# =========================================================
# LIVE PRICE
# =========================================================

hist = ticker.history(period="1d")

live_price = hist['Close'].iloc[-1]

# =========================================================
# PCR CALCULATION
# =========================================================

total_call_oi = merged_df['CALL_OI'].sum()

total_put_oi = merged_df['PUT_OI'].sum()

if total_call_oi != 0:
    pcr = total_put_oi / total_call_oi
else:
    pcr = 0

# =========================================================
# MAX PAIN
# =========================================================

merged_df['TOTAL_OI'] = (
    merged_df['CALL_OI'] +
    merged_df['PUT_OI']
)

max_pain = merged_df.loc[
    merged_df['TOTAL_OI'].idxmax(),
    'STRIKE'
]

# =========================================================
# HIGHEST OI
# =========================================================

highest_call_oi = merged_df.loc[
    merged_df['CALL_OI'].idxmax(),
    'STRIKE'
]

highest_put_oi = merged_df.loc[
    merged_df['PUT_OI'].idxmax(),
    'STRIKE'
]

# =========================================================
# MARKET VIEW
# =========================================================

market_view = "SIDEWAYS"

if pcr > 1.2:
    market_view = "🚀 BULLISH"

elif pcr < 0.8:
    market_view = "🔻 BEARISH"

# =========================================================
# DISPLAY METRICS
# =========================================================

st.subheader("📈 OPTION CHAIN METRICS")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "LIVE PRICE",
    round(live_price, 2)
)

col2.metric(
    "PCR",
    round(pcr, 2)
)

col3.metric(
    "MAX PAIN",
    max_pain
)

col4.metric(
    "MARKET VIEW",
    market_view
)

# =========================================================
# SUPPORT / RESISTANCE
# =========================================================

st.subheader("📊 SUPPORT & RESISTANCE")

col5, col6 = st.columns(2)

col5.success(
    f"🟢 SUPPORT : {highest_put_oi}"
)

col6.error(
    f"🔴 RESISTANCE : {highest_call_oi}"
)

# =========================================================
# OI BUILDUP
# =========================================================

merged_df['CALL_OI_CHANGE'] = (
    merged_df['CALL_OI'].diff()
)

merged_df['PUT_OI_CHANGE'] = (
    merged_df['PUT_OI'].diff()
)

# =========================================================
# ATM STRIKE
# =========================================================

merged_df['DISTANCE'] = abs(
    merged_df['STRIKE'] - live_price
)

atm_row = merged_df.loc[
    merged_df['DISTANCE'].idxmin()
]

# =========================================================
# ATM ANALYSIS
# =========================================================

st.subheader("🎯 ATM OPTION ANALYSIS")

col7, col8, col9, col10 = st.columns(4)

col7.metric(
    "ATM STRIKE",
    atm_row['STRIKE']
)

col8.metric(
    "CALL OI",
    int(atm_row['CALL_OI'])
)

col9.metric(
    "PUT OI",
    int(atm_row['PUT_OI'])
)

col10.metric(
    "TOTAL OI",
    int(atm_row['TOTAL_OI'])
)

# =========================================================
# AI SIGNAL
# =========================================================

st.subheader("🤖 OPTION CHAIN AI SIGNAL")

if pcr > 1.2 and live_price > highest_put_oi:

    st.success("🚀 STRONG BULLISH SIGNAL")

elif pcr < 0.8 and live_price < highest_call_oi:

    st.error("🔻 STRONG BEARISH SIGNAL")

else:

    st.warning("⚠️ SIDEWAYS MARKET")

# =========================================================
# FILTER NEAR ATM
# =========================================================

near_atm = merged_df[
    (merged_df['STRIKE'] > live_price - 1000) &
    (merged_df['STRIKE'] < live_price + 1000)
]

# =========================================================
# OPTION CHAIN TABLE
# =========================================================

st.subheader("📋 LIVE OPTION CHAIN")

st.dataframe(
    near_atm,
    use_container_width=True
)

# =========================================================
# TOP CALL WRITING
# =========================================================

st.subheader("🔴 TOP CALL WRITING")

top_calls = merged_df.sort_values(
    by='CALL_OI',
    ascending=False
).head(10)

st.dataframe(
    top_calls[[
        'STRIKE',
        'CALL_OI',
        'CALL_VOLUME'
    ]],
    use_container_width=True
)

# =========================================================
# TOP PUT WRITING
# =========================================================

st.subheader("🟢 TOP PUT WRITING")

top_puts = merged_df.sort_values(
    by='PUT_OI',
    ascending=False
).head(10)

st.dataframe(
    top_puts[[
        'STRIKE',
        'PUT_OI',
        'PUT_VOLUME'
    ]],
    use_container_width=True
)
