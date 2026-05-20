# =========================================================
# 🚀 NSE AI PRO MAX V4.0 - FULL INTEGRATED EDITION
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
    st.sidebar.warning("⚠️ Manual Mode: Auto-refresh paused.")

india_tz = pytz.timezone('Asia/Kolkata')
current_time = datetime.now(india_tz)
st.sidebar.info(f"🕒 {current_time.strftime('%d-%m-%Y %H:%M:%S')} IST")

# =========================================================
# TECHNICAL CORE INDICATORS ENGINE
# =========================================================
def calculate_indicators(df):
    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
    
    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(14, min_periods=1).mean()
    avg_loss = loss.rolling(14, min_periods=1).mean()
    rs = avg_gain / (avg_loss + 1e-10)
    df["RSI"] = 100 - (100 / (1 + rs))
    
    ema12 = df["Close"].ewm(span=12, adjust=False).mean()
    ema26 = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = ema12 - ema26
    df["MACD_SIGNAL"] = df["MACD"].ewm(span=9, adjust=False).mean()
    
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

    if latest["EMA20"] > latest["EMA50"]:
        score += 25
    else:
        score -= 25

    if 55 < latest["RSI"] < 70:
        score += 20
    elif latest["RSI"] > 75:
        score -= 15  
    elif latest["RSI"] < 30:
        score += 15  

    if latest["MACD"] > latest["MACD_SIGNAL"]:
        score += 25
    else:
        score -= 25

    if latest["Close"] > latest["VWAP"]:
        score += 20
    else:
        score -= 20

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
# 💡 TAB GENERATION CREATION LAYOUT (Crucial Fix)
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
        data = yf.download(
            ticker,
            interval=interval,
            period=period,
            progress=False,
            auto_adjust=True
        )

        if not data.empty:
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)

            data = calculate_indicators(data)
            signal, score = generate_signal(data)
            latest = data.iloc[-1]

            st.subheader("🤖 AI MODEL INSIGHTS")
            
            if "STRONG BUY" in signal:
                st.success(f"⚡ {signal} | QUANT SCORE: {score}")
            elif "BUY" in signal:
                st.success(f"{signal} | QUANT SCORE: {score}")
            elif "SELL" in signal:
                st.error(f"{signal} | QUANT SCORE: {score}")
            else:
                st.warning(f"{signal} | QUANT SCORE: {score}")

            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("LAST PRICE", f"₹ {round(float(latest['Close']), 2)}")
            c2.metric("MOMENTUM (RSI)", round(float(latest["RSI"]), 2))
            c3.metric("VWAP ANCHOR", f"₹ {round(float(latest['VWAP']), 2)}")
            c4.metric("MACD SPREAD", round(float(latest["MACD"]), 2))
            c5.metric("NET SCORING", f"{score} / 90")

            st.markdown("---")
            st.subheader(f"📈 {selected_stock} MULTI-LAYER STREAMING CHART")

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
# TAB 2: ROBUST OPTION CHAIN ANALYZER (WITH OVERRIDE SELECTORS)
# ---------------------------------------------------------
with tab2:
    st.header("📂 INSTITUTIONAL OPTION CHAIN ANALYZER")
    st.write("Upload an official NSE option chain spreadsheet file (CSV or Excel Format).")

    uploaded_file = st.file_uploader(
        "DROP DERIVATIVES DATA SHEET",
        type=["csv", "xlsx", "xls"]
    )

    if uploaded_file is not None:
        try:
            raw_df = None
            
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
                raw_df.dropna(how='all', inplace=True)
                
                # Check top rows to skip garbage data and find headers
                if not any(x in "".join(raw_df.columns.astype(str)).upper() for x in ["STRIKE", "OI", "VOLUME"]):
                    for i in range(min(12, len(raw_df))):
                        row_values = raw_df.iloc[i].astype(str).str.upper().tolist()
                        if any("STRIKE" in r or "OI" in r or "VOLUME" in r for r in row_values):
                            raw_df.columns = raw_df.iloc[i].astype(str).str.strip().str.upper()
                            raw_df = raw_df.iloc[i+1:].reset_index(drop=True)
                            break

                st.success("📊 SHEET INGESTED SUCCESSFULLY")
                
                # Format header text strings
                cols = [str(c).strip().upper() for c in raw_df.columns]
                raw_df.columns = cols

                # --- ADVANCED MANUAL SELECTOR CONTROLS ---
                st.info("🛠️ **COLUMN SPECIFICATION:** Verify or select your exact file headers below if the chart is empty:")
                col1, col2, col3 = st.columns(3)
                
                guess_strike = next((c for c in cols if "STRIKE" in c or "STRK" in c), cols[len(cols)//2])
                oi_cols = [c for c in cols if "OI" in c or "OPEN INTEREST" in c]
                
                guess_call_oi = next((c for c in oi_cols if "CALL" in c or "CE" in c), oi_cols[0] if oi_cols else cols[0])
                guess_put_oi = next((c for c in oi_cols if "PUT" in c or "PE" in c), oi_cols[-1] if oi_cols else cols[-1])

                selected_strike_col = col1.selectbox("STRIKE PRICE Column", cols, index=cols.index(guess_strike))
                selected_call_oi = col2.selectbox("CALL OI Column", cols, index=cols.index(guess_call_oi))
                selected_put_oi = col3.selectbox("PUT OI Column", cols, index=cols.index(guess_put_oi))

                with st.expander("🔍 DATA VIEW WINDOW"):
                    st.dataframe(raw_df.head(15), use_container_width=True)

                if st.button("🚀 EXECUTE DERIVATIVES VOLUME & OI QUANTS", use_container_width=True):
                    def clean_numeric(series):
                        return pd.to_numeric(series.astype(str).str.replace(',', '').str.strip(), errors='coerce').fillna(0)

                    if selected_strike_col and selected_call_oi and selected_put_oi:
                        strikes = clean_numeric(raw_df[selected_strike_col])
                        c_oi = clean_numeric(raw_df[selected_call_oi])
                        p_oi = clean_numeric(raw_df[selected_put_oi])
                        
                        # Strip summary metrics out
                        valid_mask = (strikes > 0) & ((c_oi > 0) | (p_oi > 0))
                        strikes = strikes[valid_mask]
                        c_oi = c_oi[valid_mask]
                        p_oi = p_oi[valid_mask]

                        total_call_oi = c_oi.sum()
                        total_put_oi = p_oi.sum()
                        
                        pcr = total_put_oi / total_call_oi if total_call_oi > 0 else 1.0

                        resistance_wall = strikes.iloc[c_oi.idxmax()] if not c_oi.empty else 0
                        support_wall = strikes.iloc[p_oi.idxmax()] if not p_oi.empty else 0

                        if pcr >= 1.15:
                            chain_signal = "🚀 BULLISH MOMENTUM (Strong Put Writing Support)"
                            color_alert = st.success
                        elif pcr <= 0.80:
                            chain_signal = "🔻 BEARISH MOMENTUM (Aggressive Call Overwriting)"
                            color_alert = st.error
                        else:
                            chain_signal = "⚠️ RANGEBOUND / NEUTRAL MIXOMENTUM"
                            color_alert = st.warning

                        st.subheader("🤖 OPTION CHAIN DERIVATIVE MATRIX ANALYSIS")
                        color_alert(f"🎯 AI DERIVATIVE PROFILE DIRECTION: {chain_signal}")

                        a1, a2, a3, a4 = st.columns(4)
                        a1.metric("PUT-CALL RATIO (PCR)", round(pcr, 3))
                        a2.metric("SUPPORT LEVEL (MAX PUT OI)", f"₹ {int(support_wall) if support_wall > 0 else 'N/A'}")
                        a3.metric("RESISTANCE LEVEL (MAX CALL OI)", f"₹ {int(resistance_wall) if resistance_wall > 0 else 'N/A'}")
                        a4.metric("TOTAL OPEN CONTRACTS", f"{int(total_call_oi + total_put_oi):,}")

                        # Render Chart
                        fig_chain = go.Figure()
                        fig_chain.add_trace(go.Bar(x=strikes, y=c_oi, name='Call OI (Resistance)', marker_color='#EF4444'))
                        fig_chain.add_trace(go.Bar(x=strikes, y=p_oi, name='Put OI (Support)', marker_color='#10B981'))
                        
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
                        st.error("❌ Column selection missing.")
            else:
                st.error("❌ FILE FORMAT REJECTION: Sheet is empty.")
        except Exception as e:
            st.error(f"🔴 DERIVATIVE CALCULATION SPREAD EXCEPTION ERROR: {str(e)}")

# =========================================================
# SYSTEM STABLE PRODUCTION FOOTER
# =========================================================
st.markdown("---")
st.caption("🚀 NSE AI PRO MAX V4.0 | Institutional Quantitative High-Frequency Engine")
