import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from streamlit_autorefresh import st_autorefresh

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(page_title="🔥 PRO NSE AI SCANNER V2", layout="wide")
st_autorefresh(interval=8000, key="refresh")

st.title("🔥 PRO NSE AI SCANNER (AI + OPTIONS + VOLUME STRENGTH)")

# =============================
# SECTORS
# =============================
sectors = {
    "Nifty 50": ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS"],
    "Banking": ["SBIN.NS","AXISBANK.NS","KOTAKBANK.NS","PNB.NS"],
    "IT": ["WIPRO.NS","HCLTECH.NS","TECHM.NS"],
    "Auto": ["MARUTI.NS","M&M.NS","TATAMOTORS.NS"],
    "Pharma": ["SUNPHARMA.NS","DRREDDY.NS","CIPLA.NS"],
    "Energy": ["ONGC.NS","IOC.NS"],
    "FMCG": ["ITC.NS","NESTLEIND.NS"],
    "Metals": ["TATASTEEL.NS","JSWSTEEL.NS"],
    "Power": ["NTPC.NS","POWERGRID.NS"],
    "Finance": ["BAJFINANCE.NS","BAJAJFINSV.NS"]
}

selected_sector = st.selectbox("📊 Select Sector", list(sectors.keys()))
stocks_to_scan = sectors[selected_sector]

# =============================
# DATA FETCH
# =============================
@st.cache_data(ttl=120)
def get_data(tickers):
    return yf.download(tickers, period="60d", interval="15m", group_by="ticker")

# =============================
# MODEL TRAINING
# =============================
@st.cache_resource
def train_model(X, y):
    model = RandomForestClassifier(n_estimators=80, max_depth=6)
    model.fit(X, y)
    return model

# =============================
# VOLUME STRENGTH ANALYZER (NEW)
# =============================
def get_volume_strength(df):
    recent_vol = df['Volume'].iloc[-1]
    avg_vol_20 = df['Volume'].rolling(20).mean().iloc[-1]
    
    vol_ratio = recent_vol / (avg_vol_20 + 1e-9)
    
    if vol_ratio >= 2.5:
        return "🚀 EXTRA STRONG", "Blue"
    elif vol_ratio >= 1.5:
        return "💪 STRONG", "Green"
    elif vol_ratio >= 0.8:
        return "⚖️ NORMAL", "White"
    else:
        return "⚠️ WEAK", "Red"

# =============================
# OPTIONS SENTIMENT
# =============================
def get_options_sentiment(df):
    recent = df.tail(10)
    vol_bullish = recent[recent['Close'] > recent['Open']]['Volume'].sum()
    vol_bearish = recent[recent['Close'] < recent['Open']]['Volume'].sum()
    pcr_ratio = round(vol_bullish / (vol_bearish + 1e-9), 2)
    
    if pcr_ratio > 1.5: return "🟢 CALLS STRONG", pcr_ratio
    elif pcr_ratio < 0.6: return "🔴 PUTS STRONG", pcr_ratio
    else: return "⚖️ NEUTRAL", pcr_ratio

# =============================
# ANALYSIS ENGINE
# =============================
def analyze(df):
    df = df.copy()
    
    # Indicators
    df['EMA20'] = df['Close'].ewm(span=20).mean()
    df['EMA50'] = df['Close'].ewm(span=50).mean()
    
    # RSI
    delta = df['Close'].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    rs = gain / (loss + 1e-9)
    df['RSI'] = 100 - (100 / (1 + rs))

    # MACD
    df['EMA12'] = df['Close'].ewm(span=12).mean()
    df['EMA26'] = df['Close'].ewm(span=26).mean()
    df['MACD'] = df['EMA12'] - df['EMA26']
    df['Signal'] = df['MACD'].ewm(span=9).mean()

    df.dropna(inplace=True)

    # AI Prediction Logic
    df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
    features = ['EMA20','EMA50','RSI','MACD']
    X = df[features]
    y = df['Target']
    
    if len(X) < 50: return None

    model = train_model(X, y)
    pred = model.predict(X.iloc[[-1]])[0]

    # Current Values
    price = df['Close'].iloc[-1]
    vol_status, vol_color = get_volume_strength(df)
    opt_sentiment, pcr_val = get_options_sentiment(df)
    
    support = df['Low'].tail(40).min()
    resistance = df['High'].tail(40).max()

    # CONFIDENCE SCORING
    confidence = 0
    if price > df['EMA20'].iloc[-1] > df['EMA50'].iloc[-1]: confidence += 20
    if 40 < df['RSI'].iloc[-1] < 60: confidence += 10
    if df['MACD'].iloc[-1] > df['Signal'].iloc[-1]: confidence += 15
    if pred == 1: confidence += 20
    if "STRONG" in vol_status: confidence += 20  # Added Volume Weightage
    if opt_sentiment == "🟢 CALLS STRONG": confidence += 15

    # Final Label
    if confidence >= 85: final = "🔥 HIGH PROBABILITY"
    elif confidence >= 65: final = "⚡ WATCH"
    else: final = "❌ AVOID"

    signal_text = "🟢 BUY" if pred == 1 else "🔴 SELL"
    entry = round(price, 2)
    risk = abs(price - (support if pred == 1 else resistance))
    target = round(entry + (risk * 2), 2) if pred == 1 else round(entry - (risk * 2), 2)
    stoploss = round(support, 2) if pred == 1 else round(resistance, 2)

    return final, signal_text, confidence, entry, stoploss, target, vol_status, opt_sentiment

# =============================
# SCANNER EXECUTION
# =============================
data = get_data(stocks_to_scan)
results = []

if data is not None:
    for stock in stocks_to_scan:
        try:
            df = data[stock].dropna()
            out = analyze(df)
            if out:
                final, sig, conf, ent, sl, tg, vol, opt = out
                results.append({
                    "Stock": stock,
                    "Price": ent,
                    "Signal": sig,
                    "Confidence": conf,
                    "Volume": vol,
                    "Option": opt,
                    "Entry": ent,
                    "Target": tg,
                    "Stoploss": sl,
                    "Status": final
                })
        except:
            continue

    result_df = pd.DataFrame(results).sort_values(by="Confidence", ascending=False)

    # UI DISPLAY
    st.subheader(f"📊 {selected_sector} Live Analysis")
    st.dataframe(result_df, use_container_width=True)

    # Metrics for quick view
    c1, c2, c3 = st.columns(3)
    with c1:
        st.success("🚀 HIGH VOLUME STOCKS")
        st.write(result_df[result_df["Volume"].str.contains("STRONG")][["Stock", "Volume"]])
    with c2:
        st.info("🟢 CALL POWER (BULLISH)")
        st.write(result_df[result_df["Option"] == "🟢 CALLS STRONG"][["Stock", "Option"]])
    with c3:
        st.error("⚠️ WEAK VOLUME (BE CAREFUL)")
        st.write(result_df[result_df["Volume"] == "⚠️ WEAK"][["Stock", "Volume"]])

    st.subheader("📈 Chart & Technicals")
    s_stock = st.selectbox("Pick a stock to see details", result_df["Stock"])
    st.line_chart(data[s_stock]["Close"])
