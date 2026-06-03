import streamlit as st
import pandas as pd
import yfinance as yf

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(layout="wide")
st.title("📊 NSE Option Screener (yfinance version)")

# ==========================================
# USER INPUTS
# ==========================================
symbol = st.selectbox("Select Index", ["^NSEI", "^NSEBANK"])  # NIFTY & BANKNIFTY Yahoo symbols
pcr_threshold = st.slider("PCR Threshold", 0.5, 2.0, 1.0)
volume_filter = st.number_input("Min Volume", value=1000)

# ==========================================
# FETCH OPTION DATA USING YFINANCE
# ==========================================
try:
    ticker = yf.Ticker(symbol)
    expiries = ticker.options
    st.subheader("📅 Available Expiry Dates")
    st.write(expiries)

    # Fetch first expiry for demo
    expiry = expiries[0]
    opt_chain = ticker.option_chain(expiry)
    calls = opt_chain.calls
    puts = opt_chain.puts
except Exception as e:
    st.error(f"❌ Error fetching data: {e}")
    st.stop()

# ==========================================
# MERGE CALLS & PUTS
# ==========================================
calls_df = calls[["strike", "openInterest", "volume"]].rename(columns={"openInterest": "CE_OI", "volume": "CE_Vol"})
puts_df = puts[["strike", "openInterest", "volume"]].rename(columns={"openInterest": "PE_OI", "volume": "PE_Vol"})

merged = pd.merge(calls_df, puts_df, on="strike", how="outer").fillna(0)
merged["Volume"] = merged["CE_Vol"] + merged["PE_Vol"]
merged["PCR"] = merged["PE_OI"] / merged["CE_OI"].replace(0, 1)

# ==========================================
# FILTERING
# ==========================================
filtered = merged[(merged["PCR"] >= pcr_threshold) & (merged["Volume"] >= volume_filter)]

# ==========================================
# DISPLAY RESULTS
# ==========================================
st.subheader(f"{symbol} Option Screener Results ({expiry})")
st.dataframe(filtered, use_container_width=True)

avg_pcr = merged["PCR"].mean()
if avg_pcr > 1:
    st.success(f"Market Sentiment: Bullish (PCR={avg_pcr:.2f})")
else:
    st.error(f"Market Sentiment: Bearish (PCR={avg_pcr:.2f})")
