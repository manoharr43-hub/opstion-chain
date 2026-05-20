# =========================================================
# 🚀 NSE AI PRO MAX V3.1 - EXPANDED STOCK LIST EDITION
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
    page_title="NSE AI PRO MAX V3.1",
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

# =========================================================
# TITLE
# =========================================================

st.title("🚀 NSE AI PRO MAX V3.1")
st.caption("INSTITUTIONAL EDITION + OPTIONS AI SETUP (EXPANDED STOCKS)")

# =========================================================
# 🔥 EXPANDED NSE STOCK LIST (NIFTY 50 + TOP STOCKS)
# =========================================================

nse_stocks = {
    "RELIANCE": "RELIANCE.NS",
    "HDFCBANK": "HDFCBANK.NS",
    "ICICIBANK": "ICICIBANK.NS",
    "INFY": "INFY.NS",
    "TCS": "TCS.NS",
    "SBIN": "SBIN.NS",
    "ITC": "ITC.NS",
    "LT": "LT.NS",
    "AXISBANK": "AXISBANK.NS",
    "KOTAKBANK": "KOTAKBANK.NS",
    "SUNPHARMA": "SUNPHARMA.NS",
    "BAJFINANCE": "BAJFINANCE.NS",
    "ADANIENT": "ADANIENT.NS",
    "ADANIPORTS": "ADANIPORTS.NS",
    "APOLLOHOSP": "APOLLOHOSP.NS",
    "ASIANPAINT": "ASIANPAINT.NS",
    "BAJAJ-AUTO": "BAJAJ-AUTO.NS",
    "BAJAJFINSV": "BAJAJFINSV.NS",
    "BEL": "BEL.NS",
    "BHARTIARTL": "BHARTIARTL.NS",
    "BPCL": "BPCL.NS",
    "BRITANNIA": "BRITANNIA.NS",
    "CIPLA": "CIPLA.NS",
    "COALINDIA": "COALINDIA.NS",
    "DIVISLAB": "DIVISLAB.NS",
    "DRREDDY": "DRREDDY.NS",
    "EICHERMOT": "EICHERMOT.NS",
    "GRASIM": "GRASIM.NS",
    "HCLTECH": "HCLTECH.NS",
    "HEROMOTOCO": "HEROMOTOCO.NS",
    "HINDALCO": "HINDALCO.NS",
    "HINDUNILVR": "HINDUNILVR.NS",
    "INDUSINDBK": "INDUSINDBK.NS",
    "JSWSTEEL": "JSWSTEEL.NS",
    "M&M": "M&M.NS",
    "MARUTI": "MARUTI.NS",
    "NESTLEIND": "NESTLEIND.NS",
    "NTPC": "NTPC.NS",
    "ONGC": "ONGC.NS",
    "POWERGRID": "POWERGRID.NS",
    "TATAMOTORS": "TATAMOTORS.NS",
    "TATASTEEL": "TATASTEEL.NS",
    "TECHM": "TECHM.NS",
    "TITAN": "TITAN.NS",
    "ULTRACEMCO": "ULTRACEMCO.NS",
    "WIPRO": "WIPRO.NS",
    "TRENT": "TRENT.NS"
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

# --- SCREENER KIT LINK ---
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


# =========================================================
# INDICATOR FUNCTION
# =========================================================

def calculate_indicators(df):

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    for col in ["Close", "High", "Low", "Open", "Volume"]:
        df[col] = pd.Series(df[col]).squeeze()

    df["EMA20"] = df["Close"].ewm(span=20).mean()
    df["EMA50"] = df["Close"].ewm(span=50).mean()

    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))

    ema12 = df["Close"].ewm(span=12).mean()
    ema26 = df["Close"].ewm(span=26).mean()
    df["MACD"] = ema12 - ema26
    df["MACD_SIGNAL"] = df["MACD"].ewm(span=9).mean()

    df["VWAP"] = (
        (df["Close"] * df["Volume"]).cumsum()
        / df["Volume"].cumsum()
    )

    high_low = df["High"] - df["Low"]
    high_close = np.abs(df["High"] - df["Close"].shift())
    low_close = np.abs(df["Low"] - df["Close"].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    df["ATR"] = true_range.rolling(14).mean()

    df["AVG_VOLUME"] = df["Volume"].rolling(20).mean()
    df["VOLUME_SPIKE"] = np.where(
        df["Volume"] > df["AVG_VOLUME"] * 1.5,
        "YES",
        "NO"
    )

    df = df.fillna(0)
    return df

# =========================================================
# AI SIGNAL ENGINE
# =========================================================

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

    if latest["VOLUME_SPIKE"] == "YES": score += 10

    if score >= 70: signal = "🚀 STRONG BUY"
    elif score >= 30: signal = "✅ BUY"
    elif score <= -70: signal = "🚨 STRONG SELL"
    elif score <= -30: signal = "🔻 SELL"
    else: signal = "⚠️ SIDEWAYS"

    return signal, score


# =========================================================
# TABS SETUP
# =========================================================
tab1, tab2 = st.tabs(["📈 AI Live Chart & Scanner", "📂 Upload Screener CSV & Extract AI Target"])

# =========================================================
# TAB 1: LIVE CHART & SCANNER
# =========================================================
with tab1:
    try:
        df = yf.download(
            ticker,
            interval=interval,
            period=period,
            progress=False,
            auto_adjust=True,
            group_by='column'
        )

        if df.empty:
            st.error("NO DATA FOUND")
        else:
            df = calculate_indicators(df)
            signal, score = generate_signal(df)
            latest = df.iloc[-1]
            current_price = float(latest["Close"])

            # Signal Display
            st.subheader("🤖 AI SIGNAL ENGINE")
            if "BUY" in signal: st.success(f"{signal} | SCORE : {score}")
            elif "SELL" in signal: st.error(f"{signal} | SCORE : {score}")
            else: st.warning(f"{signal} | SCORE : {score}")

            # Metrics
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("PRICE", f"₹ {round(current_price,2)}")
            c2.metric("RSI", round(float(latest["RSI"]),2))
            c3.metric("VWAP", round(float(latest["VWAP"]),2))
            c4.metric("MACD", round(float(latest["MACD"]),2))
            c5.metric("AI SCORE", score)

            # ATR Target Engine
            atr = float(latest["ATR"])
            entry = current_price
            sl = entry - atr
            target1 = entry + atr
            target2 = entry + (atr * 2)
            target3 = entry + (atr * 3)

            st.markdown("---")
            st.subheader("🎯 AI TARGET ENGINE")
            t1, t2, t3, t4, t5 = st.columns(5)
            t1.metric("ENTRY", round(entry,2))
            t2.metric("STOPLOSS", round(sl,2))
            t3.metric("TARGET 1", round(target1,2))
            t4.metric("TARGET 2", round(target2,2))
            t5.metric("TARGET 3", round(target3,2))

            st.markdown("---")
            if latest["VOLUME_SPIKE"] == "YES":
                st.success("🔥 VOLUME BLAST DETECTED")
            else:
                st.info("NORMAL VOLUME")

            # Option Chain Setup (Live Data)
            st.markdown("---")
            st.subheader(f"🔥 {selected_stock} OPTION CHAIN & AI SETUP")
            with st.spinner("Fetching Option Chain Data..."):
                yf_ticker = yf.Ticker(ticker)
                try:
                    expiries = yf_ticker.options
                except:
                    expiries = []
                
                if expiries:
                    nearest_expiry = expiries[0]
                    st.caption(f"📅 Expiry: **{nearest_expiry}**")
                    opt_chain = yf_ticker.option_chain(nearest_expiry)
                    calls_df = opt_chain.calls
                    puts_df = opt_chain.puts
                    
                    buffer = current_price * 0.05 
                    filtered_calls = calls_df[(calls_df['strike'] >= (current_price - buffer)) & (calls_df['strike'] <= (current_price + buffer))].copy()
                    filtered_puts = puts_df[(puts_df['strike'] >= (current_price - buffer)) & (puts_df['strike'] <= (current_price + buffer))].copy()
                    
                    if not filtered_calls.empty:
                        st.dataframe(filtered_calls[['strike', 'lastPrice', 'openInterest', 'volume']], use_container_width=True, hide_index=True)
                        
                        st.markdown("---")
                        st.subheader("🤖 AI MOMENTUM TRADE SETUP (LIVE)")
                        col_call, col_put = st.columns(2)
                        
                        with col_call:
                            with st.container(border=True):
                                c_idx = filtered_calls['volume'].idxmax()
                                c_data = filtered_calls.loc[c_idx]
                                c_ltp = float(c_data['lastPrice'])
                                st.markdown(f"<h4 style='text-align: center; color: #4CAF50;'>🟢 CALL SIDE: {float(c_data['strike'])} CE</h4>", unsafe_allow_html=True)
                                st.info(f"Highest Volume: {int(c_data['volume'])}")
                                ct1, ct2 = st.columns(2)
                                ct1.metric("ENTRY", f"₹ {round(c_ltp, 2)}")
                                ct2.metric("STOPLOSS", f"₹ {round(c_ltp * 0.85, 2)}")
                                ct3, ct4 = st.columns(2)
                                ct3.metric("TARGET 1", f"₹ {round(c_ltp * 1.15, 2)}")
                                ct4.metric("TARGET 2", f"₹ {round(c_ltp * 1.30, 2)}")

                        with col_put:
                            with st.container(border=True):
                                if not filtered_puts.empty:
                                    p_idx = filtered_puts['volume'].idxmax()
                                    p_data = filtered_puts.loc[p_idx]
                                    p_ltp = float(p_data['lastPrice'])
                                    st.markdown(f"<h4 style='text-align: center; color: #FF5252;'>🔴 PUT SIDE: {float(p_data['strike'])} PE</h4>", unsafe_allow_html=True)
                                    st.info(f"Highest Volume: {int(p_data['volume'])}")
                                    pt1, pt2 = st.columns(2)
                                    pt1.metric("ENTRY", f"₹ {round(p_ltp, 2)}")
                                    pt2.metric("STOPLOSS", f"₹ {round(p_ltp * 0.85, 2)}")
                                    pt3, pt4 = st.columns(2)
                                    pt3.metric("TARGET 1", f"₹ {round(p_ltp * 1.15, 2)}")
                                    pt4.metric("TARGET 2", f"₹ {round(p_ltp * 1.30, 2)}")
                                else:
                                    st.warning("No Put Data")
                    else:
                        st.warning("No Options Data found.")
                else:
                    st.warning("Options Expiries not found.")

            # Live Chart
            st.markdown("---")
            st.subheader(f"📈 {selected_stock} LIVE CHART")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines", name="Close"))
            fig.add_trace(go.Scatter(x=df.index, y=df["EMA20"], mode="lines", name="EMA20"))
            fig.add_trace(go.Scatter(x=df.index, y=df["EMA50"], mode="lines", name="EMA50"))
            
            fig.update_layout(
                template="plotly_dark",
                height=650,
                xaxis_rangeslider_visible=False
            )
            st.plotly_chart(fig, use_container_width=True)

            # AI Scanner (Scans all new stocks)
            st.markdown("---")
            st.subheader("🔥 LIVE NSE AI SCANNER")

            def scan_stock(item):
                name, tick = item
                try:
                    data = yf.download(
                        tick,
                        interval=interval,
                        period=period,
                        progress=False,
                        auto_adjust=True
                    )
                    if data.empty: return None
                    data = calculate_indicators(data)
                    sig, scr = generate_signal(data)
                    last = data.iloc[-1]
                    return {
                        "STOCK": name,
                        "PRICE": round(float(last["Close"]),2),
                        "SIGNAL": sig,
                        "SCORE": scr,
                        "RSI": round(float(last["RSI"]),2)
                    }
                except:
                    return None

            results = []
            with ThreadPoolExecutor(max_workers=15) as executor:
                scanned = executor.map(scan_stock, nse_stocks.items())

            for item in scanned:
                if item is not None:
                    results.append(item)

            scan_df = pd.DataFrame(results)
            scan_df = scan_df.sort_values(by="SCORE", ascending=False)
            st.dataframe(scan_df, use_container_width=True, hide_index=True)

            # Top Picks
            st.markdown("---")
            st.subheader("🚀 TOP AI PICKS")
            top_buys = scan_df[scan_df["SIGNAL"].str.contains("BUY")].head(5)
            st.dataframe(top_buys, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"ERROR : {str(e)}")


# =========================================================
# TAB 2: UPLOADED CSV TO CALL/PUT AI BOXES
# =========================================================
with tab2:
    try: 
        st.header("📂 Screener Kit Data Processing")
        st.write("మీరు డౌన్‌లోడ్ చేసిన Screener Excel/CSV ఫైల్ ని ఇక్కడ అప్లోడ్ చేయండి. దాని కింద AI మూమెంట్ బాక్సులు వస్తాయి.")
        
        uploaded_file = st.file_uploader("Upload Your File (CSV or Excel)", type=["csv", "xlsx", "xls"])
        
        if uploaded_file is not None:
            if uploaded_file.name.endswith('.csv'):
                screener_df = pd.read_csv(uploaded_file)
            else:
                screener_df = pd.read_excel(uploaded_file)
                
            screener_df = screener_df.dropna(how='all')
            
            st.success("✅ File Successfully Loaded!")
            st.subheader("📊 Your Uploaded Data Report")
            st.dataframe(screener_df, use_container_width=True)
            
            st.markdown("---")
            st.subheader("⚙️ Map Your Columns For AI Trade Setup")
            st.caption("మీ ఎక్సెల్ షీట్ లో కాలమ్ పేర్లు వేరుగా ఉండొచ్చు, కాబట్టి ఏ కాలమ్ దేనికి సంబంధించినదో కింద సెలెక్ట్ చేయండి.")
            
            cols = list(screener_df.columns)
            col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
            with col_m1: strike_col = st.selectbox("Strike Price Column", cols, index=0)
            with col_m2: ce_vol_col = st.selectbox("Call Volume Column", cols, index=min(1, len(cols)-1))
            with col_m3: ce_ltp_col = st.selectbox("Call LTP (Price) Column", cols, index=min(2, len(cols)-1))
            with col_m4: pe_vol_col = st.selectbox("Put Volume Column", cols, index=min(3, len(cols)-1))
            with col_m5: pe_ltp_col = st.selectbox("Put LTP (Price) Column", cols, index=min(4, len(cols)-1))
            
            if st.button("🚀 Generate AI Momentum Targets", use_container_width=True):
                screener_df[ce_vol_col] = pd.to_numeric(screener_df[ce_vol_col], errors='coerce').fillna(0)
                screener_df[pe_vol_col] = pd.to_numeric(screener_df[pe_vol_col], errors='coerce').fillna(0)
                screener_df[ce_ltp_col] = pd.to_numeric(screener_df[ce_ltp_col], errors='coerce').fillna(0)
                screener_df[pe_ltp_col] = pd.to_numeric(screener_df[pe_ltp_col], errors='coerce').fillna(0)
                screener_df[strike_col] = pd.to_numeric(screener_df[strike_col], errors='coerce').fillna(0)
                
                c_idx = screener_df[ce_vol_col].idxmax()
                c_strike = screener_df.loc[c_idx, strike_col]
                c_ltp = screener_df.loc[c_idx, ce_ltp_col]
                c_vol = screener_df.loc[c_idx, ce_vol_col]
                
                p_idx = screener_df[pe_vol_col].idxmax()
                p_strike = screener_df.loc[p_idx, strike_col]
                p_ltp = screener_df.loc[p_idx, pe_ltp_col]
                p_vol = screener_df.loc[p_idx, pe_vol_col]
                
                st.markdown("---")
                st.subheader("🤖 AI MOMENTUM TRADE SETUP (CSV DATA)")
                col_call, col_put = st.columns(2)
                
                with col_call:
                    with st.container(border=True):
                        st.markdown(f"<h3 style='text-align: center; color: #4CAF50;'>🟢 CALL SIDE: {c_strike} CE</h3>", unsafe_allow_html=True)
                        st.info(f"**Highest Volume:** {int(c_vol)}")
                        if c_ltp > 0:
                            t1, t2 = st.columns(2)
                            t1.metric("ENTRY", f"₹ {round(c_ltp, 2)}")
                            t2.metric("STOPLOSS", f"₹ {round(c_ltp * 0.85, 2)}")
                            t3, t4 = st.columns(2)
                            t3.metric("TARGET 1", f"₹ {round(c_ltp * 1.15, 2)}")
                            t4.metric("TARGET 2", f"₹ {round(c_ltp * 1.30, 2)}")
                        else:
                            st.warning("LTP is 0. Check columns.")

                with col_put:
                    with st.container(border=True):
                        st.markdown(f"<h3 style='text-align: center; color: #FF5252;'>🔴 PUT SIDE: {p_strike} PE</h3>", unsafe_allow_html=True)
                        st.info(f"**Highest Volume:** {int(p_vol)}")
                        if p_ltp > 0:
                            pt1, pt2 = st.columns(2)
                            pt1.metric("ENTRY", f"₹ {round(p_ltp, 2)}")
                            pt2.metric("STOPLOSS", f"₹ {round(p_ltp * 0.85, 2)}")
                            pt3, pt4 = st.columns(2)
                            pt3.metric("TARGET 1", f"₹ {round(p_ltp * 1.15, 2)}")
                            pt4.metric("TARGET 2", f"₹ {round(p_ltp * 1.30, 2)}")
                        else:
                            st.warning("LTP is 0. Check columns.")

    except Exception as e: 
        st.error(f"File Error: {str(e)}")

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")
st.caption("🚀 NSE AI PRO MAX V3.1 | Institutional Edition")
