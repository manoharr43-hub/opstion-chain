import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(page_title="🔥 PRO NSE OPTIONCHAIN ULTIMATE", layout="wide")
st.title("🔥 PRO NSE AI SIMULATION (OptionChain Edition)")
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
# FEATURE MODULES
# =============================

# 1. Support & Resistance
def get_pivot_points(df):
    recent = df.tail(10)
    high, low, close = recent['High'].max(), recent['Low'].min(), recent['Close'].iloc[-1]
    pivot = (high + low + close) / 3
    r1, s1 = (2 * pivot) - low, (2 * pivot) - high
    return round(s1, 2), round(r1, 2)

# 2. Big Player Detector
def get_big_player_status(df):
    avg_vol_20 = df['Volume'].rolling(20).mean().iloc[-1]
    current_vol = df['Volume'].iloc[-1]
    if current_vol > avg_vol_20 * 3:
        return "🐋 BIG PLAYER ENTRY"
    elif current_vol > avg_vol_20 * 2:
        return "🏦 INSTITUTIONAL ACTIVITY"
    else:
        return "⚖️ NORMAL VOLUME"

# 3. Calls vs Puts Strength
def get_option_strength(df):
    recent = df.tail(10)
    vol_bullish = recent[recent['Close'] >= recent['Open']]['Volume'].sum()
    vol_bearish = recent[recent['Close'] < recent['Open']]['Volume'].sum()
    pcr_ratio = round(vol_bullish / (vol_bearish + 1e-9), 2)
    if pcr_ratio > 1.8: return "🟢 CALLS STRONG", pcr_ratio
    elif pcr_ratio < 0.5: return "🔴 PUTS STRONG", pcr_ratio
    else: return "⚖️ NEUTRAL", pcr_ratio

# =============================
# CORE ANALYSIS ENGINE
# =============================
def analyze(df):
    if len(df) < 100: return None
    df['EMA20'] = df['Close'].ewm(span=20).mean()
    df['EMA50'] = df['Close'].ewm(span=50).mean()
    df['EMA200'] = df['Close'].ewm(span=200).mean()
    df.dropna(inplace=True)

    price = df['Close'].iloc[-1]
    s1, r1 = get_pivot_points(df)
    big_player = get_big_player_status(df)
    opt_sentiment, pcr_val = get_option_strength(df)

    df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
    features = ['EMA20','EMA50']
    X, y = df[features].tail(60), df['Target'].tail(60)
    if len(X) < 30: return None
    model = train_model(X, y)
    pred = model.predict(X.iloc[[-1]])[0]

    confidence = round((y.sum() / len(y)) * 100, 2) if len(y) > 0 else 0
    signal_text = "🟢 BUY" if pred == 1 else "🔴 SELL"

    return signal_text, confidence, round(price, 2), s1, r1, big_player, opt_sentiment

# =============================
# SCANNER EXECUTION
# =============================
with st.spinner(f"Scanning {selected_sector} stocks..."):
    data = get_data(stocks_to_scan)
    results = []
    if data is not None:
        for stock in stocks_to_scan:
            try:
                df_stock = data[stock].dropna() if isinstance(data.columns, pd.MultiIndex) else data.dropna()
                out = analyze(df_stock)
                if out:
                    sig, conf, price, s1, r1, big_player, opt_sentiment = out
                    results.append({
                        "Stock": stock,
                        "Price": price,
                        "Signal": sig,
                        "Confidence": conf,
                        "Support": s1,
                        "Resistance": r1,
                        "Big Player": big_player,
                        "Option Sentiment": opt_sentiment
                    })
            except Exception as e:
                continue

    if len(results) > 0:
        st.subheader(f"📊 {selected_sector} OptionChain Live Analysis")
        st.dataframe(pd.DataFrame(results), use_container_width=True)

        # NSE Sector Summary (Bottom Screen)
        buy_stocks = [r for r in results if r['Signal'] == "🟢 BUY"]
        sell_stocks = [r for r in results if r['Signal'] == "🔴 SELL"]

        st.markdown("---")
        st.subheader("📊 NSE Sector Summary (Top Strong Signals)")
        c1, c2 = st.columns(2)
        with c1:
            st.success("🟢 Strong BUY Candidates")
            if buy_stocks:
                st.dataframe(pd.DataFrame(buy_stocks)[["Stock","Price","Confidence"]], use_container_width=True)
            else:
                st.write("No Strong BUY signals right now.")
        with c2:
            st.error("🔴 Strong SELL Candidates")
            if sell_stocks:
                st.dataframe(pd.DataFrame(sell_stocks)[["Stock","Price","Confidence"]], use_container_width=True)
            else:
                st.write("No Strong SELL signals right now.")
    else:
        st.error(f"⚠️ ERROR: Could not analyze any stocks in {selected_sector} sector right now.")
        st.warning("Ensure there is enough historical data. Try changing period to '60d' and interval to '15m'.")
