import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from streamlit_autorefresh import st_autorefresh
import time

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(page_title="🔥 PRO NSE AI SCANNER ULTIMATE V6", layout="wide")
st_autorefresh(interval=10000, key="refresh") # 10 seconds refresh

st.title("🔥 PRO NSE AI SCANNER (SHORT COVERING EDITION)")
st.markdown("---")

# =============================
# SECTORS
# =============================
sectors = {
    "Nifty 50": ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS","BHARTIARTL.NS","SBIN.NS"],
    "Banking": ["SBIN.NS","AXISBANK.NS","KOTAKBANK.NS","PNB.NS","HDFCBANK.NS","ICICIBANK.NS"],
    "IT": ["WIPRO.NS","HCLTECH.NS","TECHM.NS","INFY.NS","TCS.NS"],
    "Auto": ["MARUTI.NS","M&M.NS","TATAMOTORS.NS","HEROMOTOCO.NS"],
    "Pharma": ["SUNPHARMA.NS","DRREDDY.NS","CIPLA.NS","APOLLOHOSP.NS"],
    "Energy": ["ONGC.NS","IOC.NS","BPCL.NS","GAIL.NS"],
    "FMCG": ["ITC.NS","NESTLEIND.NS","HINDUNILVR.NS"],
    "Metals": ["TATASTEEL.NS","JSWSTEEL.NS","HINDALCO.NS"],
    "Power": ["NTPC.NS","POWERGRID.NS","TATAPOWER.NS"],
    "Finance": ["BAJFINANCE.NS","BAJAJFINSV.NS","CHOLAFIN.NS"]
}

selected_sector = st.selectbox("📊 Select Sector to Scan", list(sectors.keys()))
stocks_to_scan = sectors[selected_sector]

# =============================
# DATA FETCH
# =============================
@st.cache_data(ttl=120)
def get_data(tickers):
    # Fetch enough data for 200 EMA and Pivot Points
    return yf.download(tickers, period="60d", interval="15m", group_by="ticker", threads=True)

# =============================
# MODEL TRAINING
# =============================
@st.cache_resource
def train_model(X, y):
    model = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
    model.fit(X, y)
    return model

# =============================
# ADVANCED ANALYZERS (NEW FEATURES)
# =============================

# 1. Pivot Points Support & Resistance
def get_pivot_points(df):
    recent = df.tail(10) # Using recent 15m bars to estimate daily pivots
    high = recent['High'].max()
    low = recent['Low'].min()
    close = recent['Close'].iloc[-1]
    
    pivot = (high + low + close) / 3
    r1 = (2 * pivot) - low
    s1 = (2 * pivot) - high
    
    return round(s1, 2), round(r1, 2)

# 2. Short Covering Detector (mimics logic)
def get_short_covering_status(df):
    recent_vol = df['Volume'].iloc[-1]
    avg_vol_20 = df['Volume'].rolling(20).mean().iloc[-1]
    
    vol_ratio = recent_vol / (avg_vol_20 + 1e-9)
    
    if vol_ratio >= 3.0: return "🐋 WHALE ENTRY", "Blue", 25
    elif vol_ratio >= 2.0: return "👔 INSTITUTIONAL", "Green", 15
    elif vol_ratio >= 1.0: return "⚖️ NORMAL", "White", 0
    else: return "⚠️ WEAK PARTICIPATION", "Red", -5

# 3. Option Strength Analyzer (mimics PCR)
def get_option_strength(df):
    recent = df.tail(10)
    vol_bullish = recent[recent['Close'] >= recent['Open']]['Volume'].sum()
    vol_bearish = recent[recent['Close'] < recent['Open']]['Volume'].sum()
    
    pcr_ratio = round(vol_bullish / (vol_bearish + 1e-9), 2)
    
    if pcr_ratio > 1.8: return "🟢 CALLS STRONG", pcr_ratio
    elif pcr_ratio < 0.5: return "🔴 PUTS STRONG", pcr_ratio
    else: return "⚖️ NEUTRAL", pcr_ratio

# 4. Fake Breakout/Breakdown Detector
def get_breakout_status(df, s1, r1):
    price = df['Close'].iloc[-1]
    prev_price = df['Close'].iloc[-2]
    current_vol = df['Volume'].iloc[-1]
    avg_vol_20 = df['Volume'].rolling(20).mean().iloc[-1]
    
    status = "NO BREAKOUT"
    if price > r1 and prev_price <= r1:
        status = "🚀 GENUINE BREAKOUT" if current_vol > avg_vol_20 * 1.5 else "⚠️ FAKE BREAKOUT"
    elif price < s1 and prev_price >= s1:
        status = "🔻 GENUINE BREAKDOWN" if current_vol > avg_vol_20 * 1.5 else "⚠️ FAKE BREAKDOWN"
            
    return status

# =============================
# CORE ANALYSIS ENGINE
# =============================
def analyze(df):
    df = df.copy()
    
    if len(df) < 100: return None
    
    #indicators
    df['EMA20'] = df['Close'].ewm(span=20).mean()
    df['EMA50'] = df['Close'].ewm(span=50).mean()
    df['EMA200'] = df['Close'].ewm(span=200).mean()
    
    delta = df['Close'].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    rs = gain / (loss + 1e-9)
    df['RSI'] = 100 - (100 / (1 + rs))
    
    df['EMA12'] = df['Close'].ewm(span=12).mean()
    df['EMA26'] = df['Close'].ewm(span=26).mean()
    df['MACD'] = df['EMA12'] - df['EMA26']
    df['Signal'] = df['MACD'].ewm(span=9).mean()

    df.dropna(inplace=True)

    # Values for analysis
    price = df['Close'].iloc[-1]
    
    # Call new advanced modules (Short Covering & PCR mimic)
    s1, r1 = get_pivot_points(df)
    vol_status, vol_color, vol_boost = get_short_covering_status(df)
    opt_sentiment, pcr_val = get_option_strength(df)
    breakout_status = get_breakout_status(df, s1, r1)

    # AI Prediction Logic (disturbance minimized)
    df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
    features = ['EMA20','EMA50','RSI','MACD']
    X = df[features].tail(60) # Train on recent 60 bars
    y = df['Target'].tail(60)
    
    if len(X) < 30: return None
    model = train_model(X, y)
    pred = model.predict(X.iloc[[-1]])[0]

    # Confidence Score (Weighted)
    confidence = 0
    if price > df['EMA50'].iloc[-1] > df['EMA200'].iloc[-1]: confidence += 25
    if pred == 1: confidence += 20
    if "CALLS STRONG" in opt_sentiment: confidence += 15
    if "WHALE" in vol_status: confidence += 20
    if df['MACD'].iloc[-1] > df['Signal'].iloc[-1]: confidence += 20

    final_signal = "🔥 HIGH PROBABILITY" if confidence >= 80 else "⚡ WATCH" if confidence >= 60 else "❌ AVOID"
    
    sig_text = "🟢 BUY" if pred == 1 else "🔴 SELL"
    entry = round(price, 2)
    # Target 1:2 RR based on S/R
    risk = abs(price - (s1 if pred == 1 else r1))
    target = round(entry + (risk * 2), 2) if pred == 1 else round(entry - (risk * 2), 2)
    stoploss = round(s1, 2) if pred == 1 else round(r1, 2)

    return final, sig_text, confidence, entry, stoploss, target, vol_status, opt_sentiment, breakout_status

# =============================
# SCANNER EXECUTION
# =============================
with st.spinner(f"Scanning {selected_sector} stocks..."):
    data = get_data(stocks_to_scan)
    results = []

    if data is not None:
        for stock in stocks_to_scan:
            try:
                # Fixed MultiIndex download logic
                if isinstance(data.columns, pd.MultiIndex):
                    df_stock = data[stock].dropna()
                else:
                    df_stock = data.dropna()

                if len(df_stock) < 100: continue
                
                out = analyze(df_stock)
                if out:
                    final, sig, conf, ent, sl, tg, vol, opt, breakout = out
                    results.append({
                        "Stock": stock,
                        "Price": ent,
                        "Signal": sig,
                        "Confidence": conf,
                        "Volume": vol,
                        "Option": opt,
                        "Final Status": final,
                        "Breakout": breakout,
                        "Target": tg,
                        "Stoploss": sl,
                        "df": df_stock # Keep df for charting
                    })
            except Exception as e:
                continue

    # =============================
    # UI DISPLAY (NEW V6 FIXED)
    # =============================
    if len(results) > 0:
        result_df = pd.DataFrame(results).sort_values(by="Confidence", ascending=False)

        # 1. Main DataFrame
        st.subheader(f"📊 {selected_sector} ULTIMATE Live Analysis (AI + Pivots + Vol)")
        st.dataframe(result_df.drop(columns=['df']), use_container_width=True)

        # 2. Key Insights Columns
        st.markdown("---")
        st.subheader("💡 KEY INSIGHTS")
        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.info("🐋 WHALE/INSTITUTIONAL ACTIVITY")
            whale_df = result_df[result_df["Volume"].str.contains("WHALE|INSTITUTIONAL")]
            st.dataframe(whale_df[["Stock", "Price", "Volume", "Signal"]], use_container_width=True)
            
        with c2:
            st.success("🟢 CALL POWER (Bullish Support)")
            call_df = result_df[result_df["Option"] == "🟢 CALLS STRONG"]
            st.dataframe(call_df[["Stock", "Price", "Option", "Final Status"]], use_container_width=True)
            
        with c3:
            st.warning("🔻 GENUINE BREAKDOWN ALERTS")
            bkdown_df = result_df[result_df["Breakout"] == "🔻 GENUINE BREAKDOWN"]
            st.dataframe(bkdown_df[["Stock", "Price", "Breakout", "Confidence"]], use_container_width=True)

        # 3. Charting Section
        st.markdown("---")
        st.subheader("📈 Chart & Today's Movement")
        chart_stock = st.selectbox("Pick a stock to view today's movement", result_df["Stock"])
        
        # Filter for today's data only for speed
        all_data = result_df[result_df["Stock"] == chart_stock].iloc[0]['df']
        today_data = all_data[all_data.index.date == all_data.index[-1].date()]
        st.line_chart(today_data['Close'])

    else:
        st.error(f"⚠️ **ERROR:** Could not analyze any stocks in the **{selected_sector}** sector right now.")
        st.warning("Ensure there is enough historical data. Try changing period to '60d' and interval to '15m'.")
