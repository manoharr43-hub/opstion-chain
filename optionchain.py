# =========================================================
# 🚀 NSE AI PRO MAX V3.4 - COLUMN MAPPER GUIDE INTEGRATED
# =========================================================

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
import io
import datetime
import pytz
from concurrent.futures import ThreadPoolExecutor

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="NSE AI PRO MAX V3.4",
    page_icon="🚀",
    layout="wide"
)

# =========================================================
# AUTO REFRESH
# =========================================================

if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

if time.time() - st.session_state.last_refresh > 60:
    st.session_state.last_refresh = time.time()
    st.rerun()

# =========================================================
# DARK MODE CSS
# =========================================================

st.markdown("""
<style>
.main {
    background-color: #0E1117;
    color: white;
}
.stMetric {
    background: #1E1E1E;
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #333;
}
[data-testid="stSidebar"] {
    background-color: #161A28;
}
h1,h2,h3,h4 {
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.title("🚀 NSE AI PRO MAX V3.4")
st.caption("INSTITUTIONAL EDITION + OPTIONS AI SETUP")

# =========================================================
# STOCK LIST
# =========================================================

nse_stocks = {
    "RELIANCE": "RELIANCE.NS", "HDFCBANK": "HDFCBANK.NS", "ICICIBANK": "ICICIBANK.NS",
    "INFY": "INFY.NS", "TCS": "TCS.NS", "SBIN": "SBIN.NS", "ITC": "ITC.NS",
    "LT": "LT.NS", "AXISBANK": "AXISBANK.NS", "KOTAKBANK": "KOTAKBANK.NS",
    "SUNPHARMA": "SUNPHARMA.NS", "BAJFINANCE": "BAJFINANCE.NS"
}

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("⚙️ SETTINGS")
selected_stock = st.sidebar.selectbox("SELECT STOCK", list(nse_stocks.keys()))
interval = st.sidebar.selectbox("INTERVAL", ["5m", "15m", "30m", "1h"])
period = st.sidebar.selectbox("PERIOD", ["1d", "5d", "1mo"])
ticker = nse_stocks[selected_stock]

st.sidebar.markdown("---")
st.sidebar.subheader("🔗 QUICK LINKS")
screener_link = "INSERT_YOUR_LINK_HERE" 

st.sidebar.markdown(f'''
<a href="{screener_link}" target="_blank" style="text-decoration: none;">
    <div style="background-color: #2E86C1; padding: 10px; border-radius: 5px; text-align: center; color: white; font-weight: bold; margin-bottom: 15px;">
        📊 Open NSE Screener Kit
    </div>
</a>
''', unsafe_allow_html=True)

# Helper functions
def calculate_indicators(df):
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    for col in ["Close", "High", "Low", "Open", "Volume"]:
        if col in df.columns: df[col] = pd.Series(df[col]).squeeze()
    df["EMA20"] = df["Close"].ewm(span=20).mean()
    df["EMA50"] = df["Close"].ewm(span=50).mean()
    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    df["RSI"] = 100 - (100 / (1 + (gain.rolling(14).mean() / loss.rolling(14).mean())))
    df["MACD"] = df["Close"].ewm(span=12).mean() - df["Close"].ewm(span=26).mean()
    df["MACD_SIGNAL"] = df["MACD"].ewm(span=9).mean()
    df["VWAP"] = ((df["Close"] * df["Volume"]).cumsum()) / df["Volume"].cumsum()
    df["AVG_VOLUME"] = df["Volume"].rolling(20).mean()
    df["VOLUME_SPIKE"] = np.where(df["Volume"] > df["AVG_VOLUME"] * 1.5, "YES", "NO")
    df = df.fillna(0)
    return df

def generate_signal(df):
    latest = df.iloc[-1]
    score = 0
    if latest["EMA20"] > latest["EMA50"]: score += 25
    else: score -= 25
    if latest["Close"] > latest["VWAP"]: score += 20
    else: score -= 20
    if 55 < latest["RSI"] < 70: score += 20
    elif latest["RSI"] > 75: score -= 10
    elif latest["RSI"] < 30: score += 15
    if latest["MACD"] > latest["MACD_SIGNAL"]: score += 25
    else: score -= 25
    if score >= 70: signal = "🚀 STRONG BUY"
    elif score >= 30: signal = "✅ BUY"
    elif score <= -70: signal = "🚨 STRONG SELL"
    elif score <= -30: signal = "🔻 SELL"
    else: signal = "⚠️ SIDEWAYS"
    return signal, score

# Tabs Setup
tab1, tab2 = st.tabs(["📈 AI Live Chart & Scanner", "📂 Upload Screener CSV & Extract AI Target"])

# TAB 1
with tab1:
    try:
        df = yf.download(ticker, interval=interval, period=period, progress=False, auto_adjust=True, group_by='column')
        if not df.empty:
            df = calculate_indicators(df)
            signal, score = generate_signal(df)
            latest = df.iloc[-1]
            current_price = float(latest["Close"])

            st.subheader("🤖 AI SIGNAL ENGINE")
            if "BUY" in signal: st.success(f"{signal} | SCORE : {score}")
            elif "SELL" in signal: st.error(f"{signal} | SCORE : {score}")
            else: st.warning(f"{signal} | SCORE : {score}")

            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("PRICE", f"₹ {round(current_price,2)}")
            c2.metric("RSI", round(float(latest["RSI"]),2))
            c3.metric("VWAP", round(float(latest["VWAP"]),2))
            c4.metric("MACD", round(float(latest["MACD"]),2))
            c5.metric("AI SCORE", score)

            st.markdown("---")
            st.subheader(f"📈 {selected_stock} LIVE CHART")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines", name="Close"))
            fig.update_layout(template="plotly_dark", height=350)
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Live Error: {str(e)}")

# =========================================================
# TAB 2 - RE-OPTIMIZED UPLOAD CONTROLS
# =========================================================
with tab2:
    st.header("📂 Screener Kit Data Processing")
    uploaded_file = st.file_uploader("Upload Your File (CSV or Excel)", type=["csv", "xlsx", "xls"])
    
    if uploaded_file is not None:
        screener_df = None
        try:
            if uploaded_file.name.endswith('.csv'):
                screener_df = pd.read_csv(uploaded_file, encoding='utf-8', errors='ignore')
            else:
                screener_df = pd.read_excel(uploaded_file)
        except Exception as read_err:
            try: screener_df = pd.read_csv(uploaded_file, encoding='latin1')
            except: st.error("Error file layout parsing.")

        if screener_df is not None and not screener_df.empty:
            st.success("✅ File Successfully Loaded!")
            
            # Help Box Guide to avoid wrong selections
            with st.expander("💡 కాలమ్స్ ని ఎలా సెలెక్ట్ చేయాలో ఇక్కడ చూడండి (HELP GUIDE)", expanded=True):
                st.markdown("""
                * **Strike Price Column:** మీ టేబుల్ లో మధ్యలో ఉండే స్ట్రైక్ నెంబర్ల హెడ్డింగ్ (ఉదాహరణకు: 27000, 27100).
                * **Call Volume / LTP Column:** మీ ఎక్సెల్ లో **ఎడమ వైపు (Calls)** ఉండే వాల్యూమ్ మరియు ధర(LTP) హెడ్డింగ్స్.
                * **Put Volume / LTP Column:** మీ ఎక్సెల్ లో **కుడి వైపు (Puts)** ఉండే వాల్యూమ్ మరియు ధర(LTP) హెడ్డింగ్స్.
                """)
                
            st.subheader("📊 Your Uploaded Data Report")
            st.dataframe(screener_df.head(10), use_container_width=True)
            
            st.markdown("---")
            st.subheader("⚙️ Map Your Columns For AI Trade Setup")
            
            cols = list(screener_df.columns)
            
            # Default auto search values
            def find_best_idx(keywords, col_list, default_idx=0):
                for i, c in enumerate(col_list):
                    if any(k in str(c).lower() for k in keywords):
                        return i
                return default_idx

            s_idx = find_best_idx(['strike', 'price'], cols, 0)
            cv_idx = find_best_idx(['call volume', 'c_vol', 'ce_vol', 'volume'], cols, min(1, len(cols)-1))
            cl_idx = find_best_idx(['call ltp', 'c_ltp', 'ce_ltp', 'lastprice'], cols, min(2, len(cols)-1))
            pv_idx = find_best_idx(['put volume', 'p_vol', 'pe_vol'], cols, min(3, len(cols)-1))
            pl_idx = find_best_idx(['put ltp', 'p_ltp', 'pe_ltp'], cols, min(4, len(cols)-1))

            col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
            with col_m1: strike_col = st.selectbox("Strike Price Column", cols, index=s_idx)
            with col_m2: ce_vol_col = st.selectbox("Call Volume Column", cols, index=cv_idx)
            with col_m3: ce_ltp_col = st.selectbox("Call LTP (Price) Column", cols, index=cl_idx)
            with col_m4: pe_vol_col = st.selectbox("Put Volume Column", cols, index=pv_idx)
            with col_m5: pe_ltp_col = st.selectbox("Put LTP (Price) Column", cols, index=pl_idx)
            
            if st.button("🚀 Generate AI Momentum Targets", use_container_width=True):
                try:
                    screener_df[ce_vol_col] = pd.to_numeric(screener_df[ce_vol_col], errors='coerce').fillna(0)
                    screener_df[pe_vol_col] = pd.to_numeric(screener_df[pe_vol_col], errors='coerce').fillna(0)
                    screener_df[ce_ltp_col] = pd.to_numeric(screener_df[ce_ltp_col], errors='coerce').fillna(0)
                    screener_df[pe_ltp_col] = pd.to_numeric(screener_df[pe_ltp_col], errors='coerce').fillna(0)
                    screener_df[strike_col] = pd.to_numeric(screener_df[strike_col], errors='coerce').fillna(0)
                    
                    # CALL ANALYSIS
                    c_idx = screener_df[ce_vol_col].idxmax()
                    c_strike = screener_df.loc[c_idx, strike_col]
                    c_ltp = screener_df.loc[c_idx, ce_ltp_col]
                    c_vol = screener_df.loc[c_idx, ce_vol_col]
                    
                    # PUT ANALYSIS
                    p_idx = screener_df[pe_vol_col].idxmax()
                    p_strike = screener_df.loc[p_idx, strike_col]
                    p_ltp = screener_df.loc[p_idx, pe_ltp_col]
                    p_vol = screener_df.loc[p_idx, pe_vol_col]
                    
                    st.markdown("---")
                    st.subheader("🤖 AI MOMENTUM TRADE SETUP (CSV DATA)")
                    col_call, col_put = st.columns(2)
                    
                    with col_call:
                        with st.container(border=True):
                            # Strike Validation logic to protect against negative or bad indexing
                            if c_strike <= 0 or c_ltp <= 0:
                                st.markdown("<h3 style='text-align: center; color: #4CAF50;'>🟢 CALL SIDE</h3>", unsafe_allow_html=True)
                                st.error("❌ Strike Price లేదా LTP తప్పుగా వచ్చింది! దయచేసి పైన ఉన్న 'Strike Price' మరియు 'Call LTP' డ్రాప్‌డౌన్ లను మార్చండి.")
                            else:
                                st.markdown(f"<h3 style='text-align: center; color: #4CAF50;'>🟢 CALL SIDE: {int(c_strike)} CE</h3>", unsafe_allow_html=True)
                                st.info(f"**Highest Volume:** {int(c_vol)}")
                                t1, t2 = st.columns(2)
                                t1.metric("ENTRY", f"₹ {round(c_ltp, 2)}")
                                t2.metric("STOPLOSS", f"₹ {round(c_ltp * 0.85, 2)}")
                                t3, t4 = st.columns(2)
                                t3.metric("TARGET 1", f"₹ {round(c_ltp * 1.15, 2)}")
                                t4.metric("TARGET 2", f"₹ {round(c_ltp * 1.30, 2)}")

                    with col_put:
                        with st.container(border=True):
                            if p_strike <= 0 or p_ltp <= 0:
                                st.markdown("<h3 style='text-align: center; color: #FF5252;'>🔴 PUT SIDE</h3>", unsafe_allow_html=True)
                                st.error("❌ Strike Price లేదా LTP తప్పుగా వచ్చింది! దయచేసి పైన ఉన్న 'Strike Price' మరియు 'Put LTP' డ్రాప్‌డౌన్ లను మార్చండి.")
                            else:
                                st.markdown(f"<h3 style='text-align: center; color: #FF5252;'>🔴 PUT SIDE: {int(p_strike)} PE</h3>", unsafe_allow_html=True)
                                st.info(f"**Highest Volume:** {int(p_vol)}")
                                pt1, pt2 = st.columns(2)
                                pt1.metric("ENTRY", f"₹ {round(p_ltp, 2)}")
                                pt2.metric("STOPLOSS", f"₹ {round(p_ltp * 0.85, 2)}")
                                pt3, pt4 = st.columns(2)
                                pt3.metric("TARGET 1", f"₹ {round(p_ltp * 1.15, 2)}")
                                pt4.metric("TARGET 2", f"₹ {round(p_ltp * 1.30, 2)}")
                except Exception as proc_err:
                    st.error(f"Error executing column mapping setup logic.")
