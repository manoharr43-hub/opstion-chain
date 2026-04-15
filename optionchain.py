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
st.set_page_config(page_title="🔥 PRO NSE AI SCANNER ULTIMATE V4", layout="wide")
st_autorefresh(interval=10000, key="refresh") # 10 seconds refresh

st.title("🔥 PRO NSE AI SCANNER (ULTIMATE EDITION - FIXED)")
st.markdown("---")

# =============================
# SECTORS
# =============================
sectors = {
    "Nifty 50": ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS","BHARTIARTL.NS"],
    "Banking": ["SBIN.NS","AXISBANK.NS","KOTAKBANK.NS","PNB.NS"],
    "IT": ["WIPRO.NS","HCLTECH.NS","TECHM.NS","INFY.NS"],
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
    # Standard download for safe integration
    return yf.download(tickers, period="60d", interval="15m", group_by="ticker", threads=True)

# =============================
# MODEL TRAINING
# =============================
@st.cache_resource
def train_model(X, y):
    model = RandomForestClassifier(n_estimators=80, max_depth=6)
    model.fit(X, y)
    return model

# =============================
# OPTIONCHAIN SENTIMENT (Mimic PCR)
# =============================
def get_options_sentiment(df):
    # Mimics Put-Call Sentiment using Volume/Price action over last 10 15m intervals
    recent = df.tail(10)
    vol_bullish = recent[recent['Close'] >= recent['Open']]['Volume'].sum()
    vol_bearish = recent[recent['Close'] < recent['Open']]['Volume'].sum()
    
    # ratio of Buying Vol to Selling Vol
    pcr_mimic = round(vol_bullish / (vol_bearish + 1e-9), 2)
    
    if pcr_mimic > 1.8:
        return "🟢 CALLS STRONG", pcr_mimic, "Bullish Support"
    elif pcr_mimic < 0.5:
        return "🔴 PUTS STRONG", pcr_mimic, "Bearish Resistance"
    else:
        return "⚖️ NEUTRAL", pcr_mimic, "Wait for trend"

# =============================
# ADVANCED ANALYZERS (Volume & S/R)
# =============================

# 1. Pivot Points S/R (Mimicked Daily Pivots from recent 15m intervals)
def get_pivot_points(df):
    recent = df.tail(10) # Roughly recent daily range
    high = recent['High'].max()
    low = recent['Low'].min()
    close = recent['Close'].iloc[-1]
    
    pivot = (high + low + close) / 3
    r1 = (2 * pivot) - low
    s1 = (2 * pivot) - high
    
    return round(s1, 2), round(r1, 2)

# 2. Volume Strength Analyzer (VSA mimic)
def get_volume_strength(df):
    recent_vol = df['Volume'].iloc[-1]
    avg_vol_20 = df['Volume'].rolling(20).mean().iloc[-1]
    
    vol_ratio = recent_vol / (avg_vol_20 + 1e-9)
    
    if vol_ratio >= 3.0:
        return "🐋 WHALE ENTRY", "Blue", 25
    elif vol_ratio >= 2.0:
        return "👔 INSTITUTIONAL", "Green", 15
    elif vol_ratio >= 1.0:
        return "⚖️ NORMAL", "White", 0
    else:
        return "⚠️ WEAK PARTICIPATION", "Red", -5

# 3. Fake Breakout/Breakdown Detector
def detect_fake_breakouts(df, s1, r1):
    price = df['Close'].iloc[-1]
    prev_price = df['Close'].iloc[-2]
    current_vol = df['Volume'].iloc[-1]
    avg_vol_20 = df['Volume'].rolling(20).mean().iloc[-1]
    
    status = "NO BREAKOUT"
    vol_status, _, _ = get_volume_strength(df)

    # BREAKOUT Check
    if price > r1 and prev_price <= r1:
        if current_vol > avg_vol_20 * 1.5:
            status = "🚀 GENUINE BREAKOUT"
        else:
            status = "⚠️ FAKE BREAKOUT"
            
    # BREAKDOWN Check
    elif price < s1 and prev_price >= s1:
        if current_vol > avg_vol_20 * 1.5:
            status = "🔻 GENUINE BREAKDOWN"
        else:
            status = "⚠️ FAKE BREAKDOWN"
            
    return status

# =============================
# ANALYSIS ENGINE (Fixed V4)
# =============================
def analyze(df):
    df = df.copy()
    
    # Need enough historical data for calculations
    if len(df) < 100:
        return None
    
    # Indicators
    df['EMA20'] = df['Close'].ewm(span=20).mean()
    df['EMA50'] = df['Close'].ewm(span=50).mean()
    df['EMA200'] = df['Close'].ewm(span=200).mean()
    
    # RSI & MACD
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

    # Current Values
    price = df['Close'].iloc[-1]
    vol_strength, vol_color, vol_boost = get_volume_strength(df)
    opt_sentiment, pcr_val, opt_notes = get_options_sentiment(df)
    
    # S/R calculations
    s1, r1 = get_pivot_points(df)
    breakout_status = detect_fake_breakouts(df, s1, r1)

    # AI Prediction Logic (disturbance minimized)
    df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
    features = ['EMA20','EMA50','RSI','MACD']
    X = df[features].tail(60) # Train on recent 60 bars
    y = df['Target'].tail(60)
    
    if len(X) < 30: return None # Safety check for enough data
    
    model = train_model(X, y)
    pred = model.predict(X.iloc[[-1]])[0]

    # Confidence Scoring (Weighted)
    confidence = 0
    
    # 1. Trend (25%)
    if price > df['EMA50'].iloc[-1] > df['EMA200'].iloc[-1]: confidence += 25
    
    # 2. Volume (20%)
    if "WHALE" in vol_strength or "INSTITUTIONAL" in vol_strength: confidence += 20
    
    # 3. AI Prediction (20%)
    if pred == 1: confidence += 20
    
    # 4. Option Sentiment (15%)
    if "CALLS STRONG" in opt_sentiment: confidence += 15
    
    # 5. MACD (20%)
    if df['MACD'].iloc[-1] > df['Signal'].iloc[-1]: confidence += 20

    # Final Probability Label
    if confidence >= 80: final = "🔥 HIGH PROBABILITY"
    elif confidence >= 60: final = "⚡ WATCH"
    else: final = "❌ AVOID"

    signal_text = "🟢 BUY" if pred == 1 else "🔴 SELL"
    entry = round(price, 2)
    # Target 1:2 RR based on S/R
    risk = abs(price - (s1 if pred == 1 else r1))
    target = round(entry + (risk * 2), 2) if pred == 1 else round(entry - (risk * 2), 2)
    stoploss = round(s1, 2) if pred == 1 else round(r1, 2)

    return final, signal_text, confidence, entry, stoploss, target, vol_strength, opt_sentiment, breakout_status

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
                        "Breakout Status": breakout,
                        "Final Status": final,
                        "Entry": ent,
                        "Target": tg,
                        "Stoploss": sl,
                        "df": df_stock # Keep df for charting
                    })
            except Exception as e:
                continue

    # =============================
    # UI DISPLAY (FIXED V4)
    # =============================
    if len(results) > 0:
        result_df = pd.DataFrame(results).sort_values(by="Confidence", ascending=False)

        # 1. Main DataFrame
        st.subheader(f"📊 {selected_sector} ULTIMATE Live Analysis")
        st.dataframe(result_df.drop(columns=['df']), use_container_width=True)

        # 2. Insights Summary
        st.markdown("---")
        st.subheader("💡 KEY INSIGHTS")
        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.info("🐋 WHALE/INSTITUTIONAL ENTRY")
            st.write(result_df[result_df["Volume"].str.contains("WHALE|INSTITUTIONAL")][["Stock", "Volume", "Signal"]])
            
        with c2:
            st.success("🟢 CALL SIDE STRONG (Bullish Support)")
            st.write(result_df[result_df["Option"] == "🟢 CALLS STRONG"][["Stock", "Option", "Final Status"]])
            
        with c3:
            st.warning("🔻 GENUINE BREAKDOWN ALERTS")
            st.write(result_df[result_df["Breakout Status"] == "🔻 GENUINE BREAKDOWN"][["Stock", "Breakout Status", "Confidence"]])

        # 3. Fast Charting Section (Added V4 Fixed)
        st.markdown("---")
        st.subheader("📈 FAST CHART (Today's Movement)")
        chart_stock = st.selectbox("Pick a stock to view today's movement", result_df["Stock"])
        
        # Filter for today's data only for speed
        all_data = result_df[result_df["Stock"] == chart_stock].iloc[0]['df']
        today_data = all_data[all_data.index.date == all_data.index[-1].date()]
        
        st.line_chart(today_data['Close'])

    else:
        st.error(f"⚠️ **ERROR:** Could not analyze any stocks in the **{selected_sector}** sector right now.")
        st.warning("Ensure enough historical data. Try changing period to '60d' and interval to '15m'.")
