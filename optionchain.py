import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objects as go
from datetime import datetime, timedelta

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(page_title="🔥 PRO NSE AI SCANNER V5", layout="wide")
st_autorefresh(interval=10000, key="refresh") # 10 seconds refresh

st.title("🔥 PRO NSE AI SCANNER (ADVANCED VISUALIZATION)")
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
    # Fetch 60d for indicators, but will filter for chart
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
    r2 = pivot + (high - low)
    s2 = pivot - (high - low)
    
    return round(s1, 2), round(r1, 2), round(s2, 2), round(r2, 2)

# 2. Volume Strength Analyzer (Big Player Entry)
def get_volume_strength(df):
    recent_vol = df['Volume'].iloc[-1]
    avg_vol_20 = df['Volume'].rolling(20).mean().iloc[-1]
    vol_ratio = recent_vol / (avg_vol_20 + 1e-9)
    
    if vol_ratio >= 3.0: return "🐋 WHALE ENTRY", "Blue", vol_ratio
    elif vol_ratio >= 2.0: return "👔 INSTITUTIONAL", "Green", vol_ratio
    elif vol_ratio >= 1.0: return "⚖️ NORMAL", "White", vol_ratio
    else: return "⚠️ WEAK", "Red", vol_ratio

# 3. Option Strength Analyzer (mimics PCR)
def get_option_strength(df):
    recent = df.tail(10)
    vol_bullish = recent[recent['Close'] >= recent['Open']]['Volume'].sum()
    vol_bearish = recent[recent['Close'] < recent['Open']]['Volume'].sum()
    
    pcr_ratio = round(vol_bullish / (vol_bearish + 1e-9), 2)
    
    if pcr_ratio > 1.8: return "🟢 CALLS STRONG", pcr_ratio
    elif pcr_ratio < 0.5: return "🔴 PUTS STRONG", pcr_ratio
    else: return "⚖️ NEUTRAL", pcr_ratio

# 4. Genuine/Fake Breakout Detector
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
    
    # Main Indicators
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
    
    # Call new advanced modules
    s1, r1, s2, r2 = get_pivot_points(df)
    vol_status, vol_color, vol_ratio = get_volume_strength(df)
    opt_sentiment, pcr_val = get_option_strength(df)
    breakout_status = get_breakout_status(df, s1, r1)

    # AI Prediction Logic (minimized disturbance)
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
    if "BULLISH" in breakout_status: confidence += 15
    if vol_ratio > 2: confidence += 20
    if pred == 1: confidence += 20
    if df['MACD'].iloc[-1] > df['Signal'].iloc[-1]: confidence += 20

    # Final Signal
    if confidence >= 80: final = "🔥 HIGH PROBABILITY"
    elif confidence >= 60: final = "⚡ WATCH"
    else: final = "❌ AVOID"

    sig_text = "🟢 BUY" if pred == 1 else "🔴 SELL"
    ent = round(price, 2)
    risk = abs(price - (s1 if pred == 1 else r1))
    tg = round(ent + (risk * 2), 2) if pred == 1 else round(ent - (risk * 2), 2)
    sl = round(s1, 2) if pred == 1 else round(r1, 2)

    return final, sig_text, confidence, ent, sl, tg, vol_status, opt_sentiment, breakout_status, s1, r1, s2, r2

# =============================
# CHARTING FUNCTION (NEW)
# Only Today & Previous Day Movement
# =============================
def plot_advanced_chart(df, stock_name, s1, r1, s2, r2, entry):
    # Filter for Today & Previous Day
    last_date = df.index[-1].date()
    prev_date = (last_date - timedelta(days=1))
    # Handling weekends, find the actual previous trading day
    while prev_date not in df.index.date:
        prev_date -= timedelta(days=1)
        if (last_date - prev_date).days > 7: break # Break safety
        
    chart_data = df[df.index.date >= prev_date].copy()
    
    fig = go.Figure()

    # 1. Candlestick
    fig.add_trace(go.Candlestick(x=chart_data.index,
                                 open=chart_data['Open'], high=chart_data['High'],
                                 low=chart_data['Low'], close=chart_data['Close'],
                                 name='Price'))

    # 2. Big Player Entries (Volume spikes on chart)
    avg_vol = chart_data['Volume'].rolling(20).mean()
    whale_entries = chart_data[chart_data['Volume'] > avg_vol * 3.0]
    inst_entries = chart_data[(chart_data['Volume'] > avg_vol * 2.0) & (chart_data['Volume'] <= avg_vol * 3.0)]

    fig.add_trace(go.Scatter(x=whale_entries.index, y=whale_entries['Close'],
                             mode='markers', marker=dict(symbol='triangle-up', size=12, color='blue'),
                             name='🐋 Whale Entry'))
    fig.add_trace(go.Scatter(x=inst_entries.index, y=inst_entries['Close'],
                             mode='markers', marker=dict(symbol='triangle-up', size=10, color='green'),
                             name='👔 Institutional Entry'))

    # 3. Support & Resistance Lines
    fig.add_hline(y=r1, line_dash="dash", line_color="red", annotation_text="R1", annotation_position="top right")
    fig.add_hline(y=s1, line_dash="dash", line_color="green", annotation_text="S1", annotation_position="bottom right")
    fig.add_hline(y=r2, line_dash="dot", line_color="darkred", annotation_text="R2")
    fig.add_hline(y=s2, line_dash="dot", line_color="darkgreen", annotation_text="S2")
    
    fig.add_hline(y=entry, line_width=2, line_color="white", annotation_text="Entry")

    # Layout Updates
    fig.update_layout(title=f"📈 {stock_name} (Today & Previous Day)",
                      yaxis_title="Price",
                      xaxis_title="Time",
                      xaxis_rangeslider_visible=False,
                      template="plotly_dark",
                      height=600)
    
    return fig

# =============================
# SCANNER EXECUTION
# =============================
with st.spinner(f"Scanning {selected_sector} stocks..."):
    data = get_data(stocks_to_scan)
    results = []

    if data is not None:
        for stock in stocks_to_scan:
            try:
                # Handle MultiIndex download
                if isinstance(data.columns, pd.MultiIndex):
                    df_stock = data[stock].dropna()
                else:
                    df_stock = data.dropna()

                out = analyze(df_stock)
                if out:
                    final, sig, conf, ent, sl, tg, vol, opt, breakout, s1, r1, s2, r2 = out
                    results.append({
                        "Stock": stock,
                        "Price": ent,
                        "Signal": sig,
                        "Confidence": conf,
                        "Volume": vol,
                        "Option": opt,
                        "Status": final,
                        "Breakout": breakout,
                        "Target": tg,
                        "Stoploss": sl,
                        "df": df_stock, # Keep df for charting
                        "s1": s1, "r1": r1, "s2": s2, "r2": r2
                    })
            except Exception as e:
                continue

    # =============================
    # UI DISPLAY (NEW V5)
    # =============================
    if len(results) > 0:
        result_df = pd.DataFrame(results).sort_values(by="Confidence", ascending=False)

        # 1. Main DataFrame
        st.subheader(f"📊 {selected_sector} Live Analysis (AI + Pivots + Vol)")
        st.dataframe(result_df.drop(columns=['df']), use_container_width=True)

        # 2. Advanced Charting Section
        st.markdown("---")
        st.subheader("📈 ADVANCED CHART (Supports/Big Players)")
        chart_stock = st.selectbox("Pick a stock to view today's movement & levels", result_df["Stock"])
        
        selected_data = result_df[result_df["Stock"] == chart_stock].iloc[0]
        
        # Plot advanced chart only for today/previous day
        fig = plot_advanced_chart(selected_data['df'], chart_stock, 
                                  selected_data['s1'], selected_data['r1'],
                                  selected_data['s2'], selected_data['r2'],
                                  selected_data['Price'])
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.error(f"⚠️ **ERROR:** Could not analyze any stocks in the **{selected_sector}** sector right now.")
        st.warning("Ensure there is enough historical data. Try period to '60d' and interval to '15m'.")
