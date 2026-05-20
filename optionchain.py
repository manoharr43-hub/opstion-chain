# =========================================================
# 🚀 NSE AI PRO MAX V4.0 - ULTRA STABLE EDITION (FINAL)
# =========================================================

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import pytz
from datetime import datetime

# Auto-refresh component (Optional - works without it if not installed)
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None

# =========================================================
# PAGE CONFIG & DARK THEME UI
# =========================================================
st.set_page_config(
    page_title="NSE AI PRO MAX V4.0",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main { background-color: #0E1117; color: white; }
    [data-testid="stSidebar"] { background-color: #111827; }
    .stMetric { background-color: #1F2937; padding: 15px; border-radius: 10px; border: 1px solid #374151; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
    h1, h2, h3, h4 { color: #FFFFFF !important; font-family: 'Inter', sans-serif; }
    div.stButton > button:first-child { background-color: #2563EB; color: white; border-radius: 6px; font-weight: bold; border: none; padding: 0.5rem 1rem; }
    div.stButton > button:first-child:hover { background-color: #1D4ED8; }
</style>
""", unsafe_allow_html=True)

st.title("🚀 NSE AI PRO MAX V4.0")
st.caption("Institutional AI Trading Dashboard + Smart Option Chain Analyzer")

# =========================================================
# STOCK REPOSITORY & SIDEBAR
# =========================================================
nse_stocks = {
    "RELIANCE": "RELIANCE.NS", "TCS": "TCS.NS", "INFY": "INFY.NS",
    "HDFCBANK": "HDFCBANK.NS", "ICICIBANK": "ICICIBANK.NS", "SBIN": "SBIN.NS",
    "LT": "LT.NS", "ITC": "ITC.NS", "AXISBANK": "AXISBANK.NS",
    "KOTAKBANK": "KOTAKBANK.NS", "BAJFINANCE": "BAJFINANCE.NS",
    "SUNPHARMA": "SUNPHARMA.NS", "MARUTI": "MARUTI.NS", "HINDUNILVR": "HINDUNILVR.NS"
}

st.sidebar.header("⚙️ CONTROL PANEL")
selected_stock = st.sidebar.selectbox("SELECT STOCK", list(nse_stocks.keys()))
interval = st.sidebar.selectbox("TIMEFRAME INTERVAL", ["5m", "15m", "30m", "1h"])
period = st.sidebar.selectbox("HISTORICAL PERIOD", ["1d", "5d", "1mo"])
ticker = nse_stocks[selected_stock]

st.sidebar.markdown("---")
st.sidebar.subheader("📌 ENGINE STATUS")

if st_autorefresh:
    st_autorefresh(interval=60000, key="nse_dashboard_polling")
    st.sidebar.success("🟢 LIVE REFRESH ACTIVE (60s)")
else:
    st.sidebar.warning("⚠️ Auto-Refresh Paused (Install streamlit-autorefresh)")

india_tz = pytz.timezone('Asia/Kolkata')
st.sidebar.info(f"🕒 {datetime.now(india_tz).strftime('%d-%m-%Y %H:%M:%S')} IST")

# =========================================================
# TECHNICAL INDICATORS & AI SIGNAL ENGINE
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
    df.bfill(inplace=True)
    df.fillna(0, inplace=True)
    return df

def generate_signal(latest):
    score = 0
    if latest["EMA20"] > latest["EMA50"]: score += 25
    else: score -= 25

    if 55 < latest["RSI"] < 70: score += 20
    elif latest["RSI"] > 75: score -= 15  
    elif latest["RSI"] < 30: score += 15  

    if latest["MACD"] > latest["MACD_SIGNAL"]: score += 25
    else: score -= 25

    if latest["Close"] > latest["VWAP"]: score += 20
    else: score -= 20

    if score >= 70: return "🚀 STRONG BUY", score
    elif score >= 30: return "✅ BUY", score
    elif score <= -70: return "🚨 STRONG SELL", score
    elif score <= -30: return "🔻 SELL", score
    else: return "⚠️ SIDEWAYS", score

# =========================================================
# TABS SETUP
# =========================================================
tab1, tab2 = st.tabs(["📈 AI LIVE TECHNICAL CHART", "📂 NSE OPTION CHAIN ANALYZER"])

# =========================================================
# TAB 1: LIVE CHART
# =========================================================
with tab1:
    try:
        data = yf.download(ticker, interval=interval, period=period, progress=False, auto_adjust=True)
        
        if not data.empty:
            # Fix multi-level indexing issue from new yfinance versions
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)

            data = calculate_indicators(data)
            latest = data.iloc[-1]
            signal, score = generate_signal(latest)

            st.subheader("🤖 AI MODEL INSIGHTS")
            if "BUY" in signal: st.success(f"⚡ {signal} | QUANT SCORE: {score}")
            elif "SELL" in signal: st.error(f"🔴 {signal} | QUANT SCORE: {score}")
            else: st.warning(f"🟡 {signal} | QUANT SCORE: {score}")

            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("LAST PRICE", f"₹ {round(float(latest['Close']), 2)}")
            c2.metric("RSI (14)", round(float(latest["RSI"]), 2))
            c3.metric("VWAP", f"₹ {round(float(latest['VWAP']), 2)}")
            c4.metric("MACD SPREAD", round(float(latest["MACD"]), 2))
            c5.metric("NET SCORING", f"{score} / 90")

            st.markdown("---")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=data.index, y=data["Close"], mode='lines', name='Spot Price', line=dict(color='#3B82F6', width=2)))
            fig.add_trace(go.Scatter(x=data.index, y=data["EMA20"], mode='lines', name='EMA 20 Fast', line=dict(color='#F59E0B', width=1.5, dash='dot')))
            fig.add_trace(go.Scatter(x=data.index, y=data["EMA50"], mode='lines', name='EMA 50 Slow', line=dict(color='#EF4444', width=1.5, dash='dash')))
            fig.update_layout(template="plotly_dark", height=500, hovermode="x unified", margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("❌ Market data not found for selected timeframe.")
    except Exception as e:
        st.error(f"🔴 LIVE TRACKING ERROR: {str(e)}")

# =========================================================
# TAB 2: OPTION CHAIN ANALYZER (BULLETPROOF PARSER)
# =========================================================
with tab2:
    st.header("📂 INSTITUTIONAL OPTION CHAIN ANALYZER")
    st.write("Upload official NSE option chain file (CSV / Excel).")

    uploaded_file = st.file_uploader("DROP FILE HERE", type=["csv", "xlsx", "xls"])

    if uploaded_file is not None:
        try:
            # Read purely without assuming headers to bypass pandas duplicate column merging
            if uploaded_file.name.endswith(".csv"):
                raw_df = pd.read_csv(uploaded_file, engine='python', on_bad_lines='skip', header=None)
            else:
                raw_df = pd.read_excel(uploaded_file, header=None)

            if raw_df is not None and not raw_df.empty:
                raw_df.dropna(how='all', inplace=True)

                # Find the actual row that contains the words STRIKE and OI
                header_idx = 0
                for i in range(min(15, len(raw_df))):
                    row_text = " ".join(raw_df.iloc[i].astype(str)).upper()
                    if "STRIKE" in row_text and "OI" in row_text:
                        header_idx = i
                        break
                
                # Extract headers and data body
                raw_headers = raw_df.iloc[header_idx].astype(str).str.strip().str.upper().tolist()
                data_df = raw_df.iloc[header_idx+1:].copy().reset_index(drop=True)
                data_df.dropna(how='all', inplace=True)

                # Locate center STRIKE point to split CALLS and PUTS
                strike_pos = next((i for i, h in enumerate(raw_headers) if "STRIKE" in h or "STRK" in h), len(raw_headers)//2)

                # Rename columns physically to prevent mixing
                final_columns = []
                for i, col in enumerate(raw_headers):
                    col = col.replace(" ", "_").replace(".", "")
                    if col in ['NAN', 'NONE', '']: col = f"DATA_{i}"

                    if i < strike_pos: final_columns.append(f"CALL_{col}")
                    elif i > strike_pos: final_columns.append(f"PUT_{col}")
                    else: final_columns.append("STRIKE_PRICE")

                data_df.columns = final_columns
                st.success("📊 NSE DATA DETECTED & STRUCTURED")
                
                # Column selection UI
                st.info("🛠️ **MAPPING ENGINE:** Left side mapped as CALLS, Right side mapped as PUTS.")
                col1, col2, col3 = st.columns(3)
                cols = list(data_df.columns)
                
                guess_strike = "STRIKE_PRICE" if "STRIKE_PRICE" in cols else cols[0]
                guess_call_oi = next((c for c in cols if c == "CALL_OI" or "CALL_CHNG_IN_OI" in c), cols[0])
                guess_put_oi = next((c for c in cols if c == "PUT_OI" or "PUT_CHNG_IN_OI" in c), cols[-1])

                selected_strike = col1.selectbox("STRIKE PRICE Column", cols, index=cols.index(guess_strike) if guess_strike in cols else 0)
                selected_call = col2.selectbox("CALL OI Column", cols, index=cols.index(guess_call_oi) if guess_call_oi in cols else 0)
                selected_put = col3.selectbox("PUT OI Column", cols, index=cols.index(guess_put_oi) if guess_put_oi in cols else 0)

                with st.expander("🔍 VIEW CLEANED MATRIX DATA"):
                    st.dataframe(data_df.head(10), use_container_width=True)

                # Execution Engine
                if st.button("🚀 EXECUTE AI QUANTS", use_container_width=True):
                    def clean_num(series):
                        return pd.to_numeric(series.astype(str).str.replace(',', '').str.strip(), errors='coerce').fillna(0)

                    if selected_strike and selected_call and selected_put:
                        strikes = clean_num(data_df[selected_strike])
                        c_oi = clean_num(data_df[selected_call])
                        p_oi = clean_num(data_df[selected_put])
                        
                        # Filter out empty/total rows at the bottom
                        valid_mask = (strikes > 0) & ((c_oi > 0) | (p_oi > 0))
                        strikes, c_oi, p_oi = strikes[valid_mask], c_oi[valid_mask], p_oi[valid_mask]

                        total_c_oi = c_oi.sum()
                        total_p_oi = p_oi.sum()
                        pcr = total_p_oi / total_c_oi if total_c_oi > 0 else 1.0

                        resistance = strikes.iloc[c_oi.idxmax()] if not c_oi.empty else 0
                        support = strikes.iloc[p_oi.idxmax()] if not p_oi.empty else 0

                        if pcr >= 1.15: signal, color = "🚀 BULLISH (Strong Put Support)", st.success
                        elif pcr <= 0.85: signal, color = "🔻 BEARISH (Call Overwriting)", st.error
                        else: signal, color = "⚠️ RANGEBOUND / NEUTRAL", st.warning

                        st.subheader("🤖 DERIVATIVE MATRIX REPORT")
                        color(f"🎯 DIRECTION: {signal}")

                        m1, m2, m3, m4 = st.columns(4)
                        m1.metric("PUT-CALL RATIO (PCR)", round(pcr, 2))
                        m2.metric("SUPPORT (MAX PUT OI)", f"₹ {int(support)}")
                        m3.metric("RESISTANCE (MAX CALL OI)", f"₹ {int(resistance)}")
                        m4.metric("TOTAL OPEN CONTRACTS", f"{int(total_c_oi + total_p_oi):,}")

                        # Bar Chart
                        fig_bar = go.Figure()
                        fig_bar.add_trace(go.Bar(x=strikes, y=c_oi, name='Call OI (Resistance)', marker_color='#EF4444'))
                        fig_bar.add_trace(go.Bar(x=strikes, y=p_oi, name='Put OI (Support)', marker_color='#10B981'))
                        fig_bar.update_layout(template="plotly_dark", barmode='group', height=450, title="OPEN INTEREST WALLS", xaxis_title="Strike Price", yaxis_title="OI Contracts")
                        st.plotly_chart(fig_bar, use_container_width=True)
                    else:
                        st.error("❌ Missing required columns.")
        except Exception as e:
            st.error(f"🔴 DATA PARSING ERROR: {str(e)}")
