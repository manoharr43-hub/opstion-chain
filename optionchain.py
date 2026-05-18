# =========================================================
# 🚀 NSE AI PRO MAX - OPTION CHAIN ANALYZER V2
# FULL WORKING VERSION
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
    page_title="NSE OPTION CHAIN ANALYZER",
    layout="wide"
)

# =========================================================
# TITLE
# =========================================================

st.title("📊 NSE OPTION CHAIN ANALYZER")
st.caption("AI BASED NSE OPTION CHAIN ANALYSIS")

# =========================================================
# STOCK LIST
# =========================================================

option_stocks = {

    "RELIANCE": "RELIANCE.NS",
    "SBIN": "SBIN.NS",
    "ICICIBANK": "ICICIBANK.NS",
    "HDFCBANK": "HDFCBANK.NS",
    "INFY": "INFY.NS",
    "TCS": "TCS.NS",
    "ITC": "ITC.NS",
    "LT": "LT.NS",
    "AXISBANK": "AXISBANK.NS",
    "TATAMOTORS": "TATAMOTORS.NS"
}

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("⚙️ SETTINGS")

selected_stock = st.sidebar.selectbox(
    "SELECT STOCK",
    list(option_stocks.keys())
)

ticker_symbol = option_stocks[selected_stock]

# =========================================================
# GET TICKER
# =========================================================

ticker = yf.Ticker(ticker_symbol)

# =========================================================
# OPTION EXPIRY FETCH
# =========================================================

try:

    expiry_dates = ticker.options

    if expiry_dates is None or len(expiry_dates) == 0:

        st.error("❌ NO OPTION DATA AVAILABLE")

        st.info("TRY ANOTHER STOCK")

        st.stop()

except Exception as e:

    st.error("❌ OPTION CHAIN FETCH FAILED")

    st.code(str(e))

    st.stop()

# =========================================================
# EXPIRY SELECTION
# =========================================================

selected_expiry = st.sidebar.selectbox(
    "SELECT EXPIRY",
    expiry_dates
)

# =========================================================
# DOWNLOAD OPTION CHAIN
# =========================================================

try:

    option_chain = ticker.option_chain(selected_expiry)

    calls = option_chain.calls
    puts = option_chain.puts

except Exception as e:

    st.error("OPTION CHAIN DOWNLOAD FAILED")

    st.code(str(e))

    st.stop()

# =========================================================
# EMPTY CHECK
# =========================================================

if calls.empty or puts.empty:

    st.error("EMPTY OPTION CHAIN")

    st.stop()

# =========================================================
# CALL DATA
# =========================================================

call_df = calls[[
    'strike',
    'lastPrice',
    'volume',
    'openInterest',
    'impliedVolatility'
]]

call_df.columns = [
    'STRIKE',
    'CALL_LTP',
    'CALL_VOLUME',
    'CALL_OI',
    'CALL_IV'
]

# =========================================================
# PUT DATA
# =========================================================

put_df = puts[[
    'strike',
    'lastPrice',
    'volume',
    'openInterest',
    'impliedVolatility'
]]

put_df.columns = [
    'STRIKE',
    'PUT_LTP',
    'PUT_VOLUME',
    'PUT_OI',
    'PUT_IV'
]

# =========================================================
# MERGE OPTION DATA
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
# PCR
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
# SUPPORT / RESISTANCE
# =========================================================

support = merged_df.loc[
    merged_df['PUT_OI'].idxmax(),
    'STRIKE'
]

resistance = merged_df.loc[
    merged_df['CALL_OI'].idxmax(),
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
# METRICS
# =========================================================

st.subheader("📈 OPTION CHAIN METRICS")

col1, col2, col3, col4, col5 = st.columns(5)

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
    "SUPPORT",
    support
)

col5.metric(
    "RESISTANCE",
    resistance
)

# =========================================================
# MARKET VIEW
# =========================================================

st.subheader("🤖 AI MARKET VIEW")

if "BULLISH" in market_view:

    st.success(market_view)

elif "BEARISH" in market_view:

    st.error(market_view)

else:

    st.warning(market_view)

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

st.subheader("🎯 ATM ANALYSIS")

col6, col7, col8, col9 = st.columns(4)

col6.metric(
    "ATM STRIKE",
    atm_row['STRIKE']
)

col7.metric(
    "CALL OI",
    int(atm_row['CALL_OI'])
)

col8.metric(
    "PUT OI",
    int(atm_row['PUT_OI'])
)

col9.metric(
    "TOTAL OI",
    int(atm_row['TOTAL_OI'])
)

# =========================================================
# AI SIGNAL
# =========================================================

st.subheader("🚀 OPTION CHAIN AI SIGNAL")

if pcr > 1.2 and live_price > support:

    st.success("🚀 STRONG BULLISH")

elif pcr < 0.8 and live_price < resistance:

    st.error("🔻 STRONG BEARISH")

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

# =========================================================
# OI CHART
# =========================================================

st.subheader("📊 OPEN INTEREST CHART")

chart_df = near_atm.copy()

fig = go.Figure()

# CALL OI

fig.add_trace(go.Bar(
    x=chart_df['STRIKE'],
    y=chart_df['CALL_OI'],
    name='CALL OI'
))

# PUT OI

fig.add_trace(go.Bar(
    x=chart_df['STRIKE'],
    y=chart_df['PUT_OI'],
    name='PUT OI'
))

fig.update_layout(

    height=600,

    barmode='group',

    xaxis_title='STRIKE PRICE',

    yaxis_title='OPEN INTEREST'
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =========================================================
# IV ANALYSIS
# =========================================================

st.subheader("📉 IMPLIED VOLATILITY")

avg_call_iv = merged_df['CALL_IV'].mean()

avg_put_iv = merged_df['PUT_IV'].mean()

col10, col11 = st.columns(2)

col10.metric(
    "AVG CALL IV",
    round(avg_call_iv, 2)
)

col11.metric(
    "AVG PUT IV",
    round(avg_put_iv, 2)
)

# =========================================================
# RAW DATA
# =========================================================

with st.expander("📄 FULL OPTION CHAIN DATA"):

    st.dataframe(
        merged_df,
        use_container_width=True
    )

# =========================================================
# FOOTER
# =========================================================

st.caption("🚀 NSE AI PRO MAX OPTION CHAIN ANALYZER")
