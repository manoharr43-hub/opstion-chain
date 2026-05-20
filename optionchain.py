# =========================================================
# 🚀 NSE AI PRO MAX V4.0 - ULTRA STABLE PRODUCTION EDITION
# =========================================================

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
import io
import pytz
from datetime import datetime

# Safe import for background autorefresh component
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None

# =========================================================
# PAGE CONFIG & LAYOUT
# =========================================================
st.set_page_config(
    page_title="NSE AI PRO MAX V4.0",
    page_icon="🚀",
    layout="wide"
)

# Custom Dark Matrix UI Theme
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
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #374151;
}
h1, h2, h3, h4, h5, h6 {
    color: #FFFFFF !important;
}
div.stButton > button:first-child {
    background-color: #2563EB;
    color: white;
    border-radius: 6px;
    border: none;
    font-weight: bold;
}
div.stButton > button:first-child:hover {
    background-color: #1D4ED8;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# Title Header
st.title("🚀 NSE AI PRO MAX V4.0")
st.caption("Institutional AI Trading Dashboard + Smart Option Chain Analyzer")

# =========================================================
# NSE STOCK REPOSITORY
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
    "AXISBANK": "AXISBANK.NS",
    "KOTAKBANK": "KOTAKBANK.NS",
    "BAJFINANCE": "BAJFINANCE.NS",
    "SUNPHARMA": "SUNPHARMA.NS",
    "MARUTI": "MARUTI.NS",
    "HINDUNILVR": "HINDUNILVR.NS"
}

# =========================================================
# SIDEBAR CONTROL PANEL
# =========================================================
st.sidebar.header("⚙️ CONTROL PANEL")

selected_stock = st.sidebar.selectbox(
    "SELECT STOCK",
    list(nse_stocks.keys())
)

interval = st.sidebar.selectbox(
    "TIMEFRAME INTERVAL",
    ["5m", "15m", "30m", "1h"]
)

period = st.sidebar.selectbox(
    "HISTORICAL PERIOD",
    ["1d", "5d", "1mo"]
)

ticker = nse_stocks[selected_stock]
st.sidebar.markdown("---")

# Active 60-Second Frontend Autorefresh Polling Engine
st.sidebar.subheader("📌 ENGINE STATUS")
if st_autorefresh:
    st_autorefresh(interval=60000, key="nse_dashboard_polling")
    st.sidebar.success("🟢 LIVE REFRESH ACTIVE (60s)")
else:
    st.sidebar.warning("⚠️ Manual Mode: Install 'streamlit-autorefresh' for automatic updates.")

india_tz = pytz.timezone('Asia/Kolkata')
current_time = datetime.now(india_tz)
st.sidebar.info(f"🕒 {current_time.strftime('%d-%m-%Y %H:%M:%S')} IST")

# =========================================================
# TECHNICAL CORE INDICATORS ENGINE
# =========================================================
def calculate_indicators(df):
    # Core Trend Tracking
    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
    
    # Momentum RSI Engine
    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(14, min_periods=1).mean()
    avg_loss = loss.rolling(14, min_periods=1).mean()
    rs = avg_gain / (avg_loss + 1e-10)
    df["RSI"] = 100 - (100 / (1 + rs))
    
    # Trend Convergence MACD Engine
    ema12 = df["Close"].ewm(span=12, adjust=False).mean()
    ema26 = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = ema12 - ema26
    df["MACD_SIGNAL"] = df["MACD"].ewm(span=9, adjust=False).mean()
    
    # Intraday Volume Weighted Average Price (VWAP)
    df["VWAP"] = (df["Close"] * df["Volume"]).cumsum() / (df["Volume"].cumsum() + 1e-10)
    
    df.fillna(method='bfill', inplace=True)
    df.fillna(0, inplace=True)
    return df

# =========================================================
# AI MULTI-FACTOR SIGNAL MATRIX ENGINE
# =========================================================
def generate_signal(df):
    latest = df.iloc[-1]
    score = 0

    # Trend Direction Rules (Weight: 25%)
    if latest["EMA20"] > latest["EMA50"]:
        score += 25
    else:
        score -= 25

    # Momentum Overbought/Oversold Rules (Weight: 20%)
    if 55 < latest["RSI"] < 70:
        score += 20
    elif latest["RSI"] > 75:
        score -= 15  # Excessive overbought pull-back risk
    elif latest["RSI"] < 30:
        score += 15  # Oversold demand surge potential

    # Structural Momentum Rules (Weight: 25%)
    if latest["MACD"] > latest["MACD_SIGNAL"]:
        score += 25
    else:
        score -= 25

    # Liquid Volume Benchmark Rules (Weight: 20%)
    if latest["Close"] > latest["VWAP"]:
        score += 20
    else:
        score -= 20

    # Final Classification Breakdown
    if score >= 70:
        signal = "🚀 STRONG BUY"
    elif score >= 30:
        signal = "✅ BUY"
    elif score <= -70:
        signal = "🚨 STRONG SELL"
    elif score <= -30:
        signal = "🔻 SELL"
    else:
        signal = "⚠️ SIDEWAYS / NEUTRAL"

    return signal, score

# =========================================================
# STREAMLIT INTERFACE FRAMEWORK WORKSPACE
# =========================================================
tab1, tab2 = st.tabs([
    "📈 AI LIVE TECHNICAL CHART",
    "📂 INSTITUTIONAL OPTION CHAIN ANALYZER"
])

# ---------------------------------------------------------
# TAB 1: ADVANCED LIVE TECHNICAL DATA VISUALIZER
# ---------------------------------------------------------
with tab1:
    try:
        # Fetching market data layers via yfinance API
        data = yf.download(
            ticker,
            interval=interval,
            period=period,
            progress=False,
            auto_adjust=True
        )

        if not data.empty:
            # Flatten multi-index output variations from yfinance formatting
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)

            # Execution Pipeline
            data = calculate_indicators(data)
            signal, score = generate_signal(data)
            latest = data.iloc[-1]

            st.subheader("🤖 AI MODEL INSIGHTS")
            
            # Contextual Status Card Container
            if "STRONG BUY" in signal:
                st.success(f"⚡ {signal} | QUANT SCORE: {score}")
            elif "BUY" in signal:
                st.success(f"{signal} | QUANT SCORE: {score}")
            elif "SELL" in signal:
                st.error(f"{signal} | QUANT SCORE: {score}")
            else:
                st.warning(f"{signal} | QUANT SCORE: {score}")

            # Top-Level Quantitative Metrics Grid
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("LAST PRICE", f"₹ {round(float(latest['Close']), 2)}")
            c2.metric("MOMENTUM (RSI)", round(float(latest["RSI"]), 2))
            c3.metric("VWAP ANCHOR", f"₹ {round(float(latest['VWAP']), 2)}")
            c4.metric("MACD SPREAD", round(float(latest["MACD"]), 2))
            c5.metric("NET SCORING", f"{score} / 90")

            st.markdown("---")
            st.subheader(f"📈 {selected_stock} MULTI-LAYER STREAMING CHART")

            # Plotly Institutional Grade Chart Configuration
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=data.index, y=data["Close"], mode='lines', name='Spot Price', line=dict(color='#3B82F6', width=2)))
            fig.add_trace(go.Scatter(x=data.index, y=data["EMA20"], mode='lines', name='EMA 20 Fast', line=dict(color='#F59E0B', width=1.5, dash='dot')))
            fig.add_trace(go.Scatter(x=data.index, y=data["EMA50"], mode='lines', name='EMA 50 Slow', line=dict(color='#EF4444', width=1.5, dash='dash')))
            
            fig.update_layout(
                template="plotly_dark",
                height=550,
                hovermode="x unified",
                margin=dict(l=20, r=20, t=30, b=20),
                paper_bgcolor="#0E1117",
                plot_bgcolor="#0E1117"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("❌ Selected asset returned empty market matrix framework from API.")
            
    except Exception as e:
        st.error(f"🔴 CRITICAL LIVE TRACKING INTERRUPT: {str(e)}")

# ---------------------------------------------------------
# TAB 2: SMART OPTION CHAIN DERIVATIVES CORE
# ---------------------------------------------------------
with tab2:
    st.header("📂 INSTITUTIONAL OPTION CHAIN ANALYZER")
    st.write("Upload an official NSE option chain spreadsheet file (CSV or Excel Format).")

    uploaded_file = st.file_uploader(
        "DROP DEERIVATIVES DATA SHEET",
        type=["csv", "xlsx", "xls"]
    )

    if uploaded_file is not None:
        try:
            raw_df = None
            
            # File Parsing Interface System
            if uploaded_file.name.endswith(".csv"):
                for enc in ["utf-8", "latin-1", "cp1252"]:
                    try:
                        uploaded_file.seek(0)
                        raw_df = pd.read_csv(uploaded_file, engine='python', encoding=enc, on_bad_lines='skip')
                        break
                    except:
                        continue
            else:
                raw_df = pd.read_excel(uploaded_file, engine="openpyxl")

            if raw_df is not None and not raw_df.empty:
                # Clean up structure bounds
                raw_df.dropna(how='all', inplace=True)
                st.success("📊 SHEET INGESTED SUCCESSFULLY")
                
                with st.expander("🔍 RAW DATAFRAME MATRIX SPECTROMETER (TOP 15 ROWS)"):
                    st.dataframe(raw_df.head(15), use_container_width=True)

                if st.button("🚀 EXECUTE DERIVATIVES VOLUME & OI QUANTS", use_container_width=True):
                    # Standardizing string formatting to clear indexing names
                    cols = [str(c).strip().upper() for c in raw_df.columns]
                    raw_df.columns = cols

                    # Clean numeric translation layer helper
                    def clean_numeric(series):
                        return pd.to_numeric(series.astype(str).str.replace(',', '').str.strip(), errors='coerce').fillna(0)

                    # Dynamic structural heuristic mapper for column tracking
                    strike_col = next((c for c in cols if "STRIKE" in c), None)
                    
                    # Track distinct Call vs Put structural boundaries
                    oi_cols = [c for c in cols if "OI" in c or "OPEN INTEREST" in c]
                    vol_cols = [c for c in cols if "VOL" in c or "VOLUME" in c]

                    call_oi, put_oi = None, None
                    call_vol, put_vol = None, None

                    # Mapping standard left/right symmetric layouts
                    if len(oi_cols) >= 2:
                        call_oi = next((c for c in oi_cols if "CALL" in c), oi_cols[0])
                        put_oi = next((c for c in oi_cols if "PUT" in c), oi_cols[-1])
                    if len(vol_cols) >= 2:
                        call_vol = next((c for c in vol_cols if "CALL" in c), vol_cols[0])
                        put_vol = next((c for c in vol_cols if "PUT" in c), vol_cols[-1])

                    # Execution Safety Gates Verification
                    if strike_col and call_oi and put_oi:
                        strikes = clean_numeric(raw_df[strike_col])
                        c_oi = clean_numeric(raw_df[call_oi])
                        p_oi = clean_numeric(raw_df[put_oi])
                        
                        c_vol = clean_numeric(raw_df[call_vol]) if call_vol else pd.Series(0, index=raw_df.index)
                        p_vol = clean_numeric(raw_df[put_vol]) if put_vol else pd.Series(0, index=raw_df.index)

                        # Core Math Calculations Engine
                        total_call_oi = c_oi.sum()
                        total_put_oi = p_oi.sum()
                        
                        # Put-Call Ratio (PCR Calculation)
                        pcr = total_put_oi / total_call_oi if total_call_oi > 0 else 1.0

                        # Locate Major Support and Resistance walls based on Highest Concentration of Open Interest
                        max_call_oi_idx = c_oi.idxmax()
                        max_put_oi_idx = p_oi.idxmax()

                        resistance_wall = strikes.iloc[max_call_oi_idx]
                        support_wall = strikes.iloc[max_put_oi_idx]

                        # Derivative Momentum Direction Classifications
                        if pcr >= 1.15:
                            chain_signal = "🚀 BULLISH MOMENTUM (Strong Put Writing Support)"
                            color_alert = st.success
                        elif pcr <= 0.80:
                            chain_signal = "🔻 BEARISH MOMENTUM (Aggressive Call Overwriting)"
                            color_alert = st.error
                        else:
                            chain_signal = "⚠️ RANGEBOUND / NEUTRAL MIXED MOMENTUM"
                            color_alert = st.warning

                        # Visual Output Metrics Reporting Panel
                        st.subheader("🤖 OPTION CHAIN DERIVATIVE MATRIX ANALYSIS")
                        color_alert(f"🎯 AI DERIVATIVE PROFILE DIRECTION: {chain_signal}")

                        a1, a2, a3, a4 = st.columns(4)
                        a1.metric("PUT-CALL RATIO (PCR)", round(pcr, 3))
                        a2.metric("LIQUID OPEN INTEREST SUPPORT", f"₹ {int(support_wall) if support_wall > 0 else 'N/A'}")
                        a3.metric("LIQUID OPEN INTEREST RESISTANCE", f"₹ {int(resistance_wall) if resistance_wall > 0 else 'N/A'}")
                        a4.metric("TOTAL POSITION OPEN VOLUME", f"{int(total_call_oi + total_put_oi):,}")

                        # Graphic Distribution Visual Mapping Block
                        fig_chain = go.Figure()
                        fig_chain.add_trace(go.Bar(x=strikes, y=c_oi, name='Call OI (Resistance Track)', marker_color='#EF4444'))
                        fig_chain.add_trace(go.Bar(x=strikes, y=p_oi, name='Put OI (Support Track)', marker_color='#10B981'))
                        
                        fig_chain.update_layout(
                            template="plotly_dark",
                            barmode='group',
                            height=450,
                            title="REAL-TIME OPEN INTEREST CONCENTRIC WALLS BY STRIKE PRICE",
                            xaxis_title="Strike Price Target",
                            yaxis_title="Open Interest Contracts Stack",
                            paper_bgcolor="#0E1117",
                            plot_bgcolor="#0E1117"
                        )
                        st.plotly_chart(fig_chain, use_container_width=True)

                    else:
                        st.error("❌ CRITICAL INGESTION TIMEOUT: Failed to find symmetrically indexed STRIKE, CALL OI, or PUT OI data parameters in sheet formatting structures.")
            else:
                st.error("❌ FILE FORMAT REJECTION: Matrix processing system returned blank rows on initialization.")
        except Exception as e:
            st.error(f"🔴 DERIVATIVE CALCULATION SPREAD EXCEPTION ERROR: {str(e)}")

# =========================================================
# SYSTEM STABLE PRODUCTION FOOTER
# =========================================================
st.markdown("---")
st.caption("🚀 NSE AI PRO MAX V4.0 | Institutional Quantitative High-Frequency Engine")
