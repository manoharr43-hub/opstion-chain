import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objects as go

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(page_title="🚀 PRO AI TRADING HUB V8", layout="wide")
st_autorefresh(interval=60000, key="refresh")

st.title("🚀 PRO NSE AI SCANNER (BIG PLAYER & CHART EDITION)")

# =============================
# NSE SECTORS (Expanded)
# =============================
sectors = {
    "Nifty 50": ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS","BHARTIARTL.NS","SBIN.NS"],
    "Banking": ["HDFCBANK.NS","ICICIBANK.NS","SBIN.NS","AXISBANK.NS","KOTAKBANK.NS","PNB.NS","CANBK.NS"],
    "IT": ["TCS.NS","INFY.NS","WIPRO.NS","HCLTECH.NS","TECHM.NS","LTIM.NS"],
    "Auto": ["TATAMOTORS.NS","M&M.NS","MARUTI.NS","EICHERMOT.NS","ASHOKLEY.NS"],
    "Metal": ["TATASTEEL.NS","HINDALCO.NS","JINDALSTEL.NS","VEDL.NS"]
}

col1, col2 = st.columns([1, 1])
with col1:
    selected_sector = st.selectbox("📊 Select NSE Sector", list(sectors.keys()))
    stocks_to_scan = sectors[selected_sector]
with col2:
    selected_stock_chart = st.selectbox("📈 View Chart for", stocks_to_scan)

# =============================
# CORE FUNCTIONS
# =============================
@st.cache_data(ttl=60)
def get_data(tickers):
    return yf.download(tickers, period="60d", interval="15m", group_by="ticker", threads=True)

def calculate_advanced_metrics(df):
    df = df.copy()
    # Basic Indicators
    df['EMA20'] = df['Close'].ewm(span=20).mean()
    df['EMA50'] = df['Close'].ewm(span=50).mean()
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # Support & Resistance (Pivot Points style)
    df['Support'] = df['Low'].rolling(window=20).min()
    df['Resistance'] = df['High'].rolling(window=20).max()

    # Big Player Activity (Volume Spike)
    avg_vol = df['Volume'].rolling(window=20).mean()
    df['BigPlayer'] = np.where(df['Volume'] > (avg_vol * 2), "⚠️ ACTIVE", "Normal")
    
    return df

# =============================
# SCANNER LOGIC
# =============================
st.subheader(f"🔍 Market Analysis: {selected_sector}")
raw_data = get_data(stocks_to_scan)
scan_results = []

for ticker in stocks_to_scan:
    try:
        df = raw_data[ticker].copy() if len(stocks_to_scan) > 1 else raw_data.copy()
        df = calculate_advanced_metrics(df).dropna()
        
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Trend Analysis
        price = round(last['Close'], 2)
        change = round(((price - prev['Close'])/prev['Close'])*100, 2)
        
        # Strong Buy/Sell Logic
        if last['Close'] > last['EMA20'] and last['RSI'] > 60:
            signal = "STRONG BUY 🔥"
            side = "CALL SIDE 🟢"
        elif last['Close'] < last['EMA20'] and last['RSI'] < 40:
            signal = "STRONG SELL 🧊"
            side = "PUT SIDE 🔴"
        else:
            signal = "NEUTRAL ⚖️"
            side = "WAIT ⏳"

        scan_results.append({
            "Stock": ticker,
            "Price": price,
            "Change %": change,
            "Signal": signal,
            "Side": side,
            "Big Player": last['BigPlayer'],
            "Support": round(last['Support'], 2),
            "Resistance": round(last['Resistance'], 2),
            "RSI": round(last['RSI'], 1)
        })
    except: continue

# Display Table
if scan_results:
    res_df = pd.DataFrame(scan_results)
    def color_signal(val):
        if "BUY" in str(val): return 'background-color: #006400; color: white'
        if "SELL" in str(val): return 'background-color: #8B0000; color: white'
        return ''
    
    st.table(res_df.style.map(color_signal, subset=['Signal']))

# =============================
# CHART SECTION (Interactive)
# =============================
st.markdown("---")
st.subheader(f"📈 Price Chart: {selected_stock_chart}")

chart_df = raw_data[selected_stock_chart].copy() if len(stocks_to_scan) > 1 else raw_data.copy()
chart_df = calculate_advanced_metrics(chart_df)

fig = go.Figure()
# Candlestick
fig.add_trace(go.Candlestick(x=chart_df.index, open=chart_df['Open'], high=chart_df['High'], low=chart_df['Low'], close=chart_df['Close'], name="Price"))
# Indicators
fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df['EMA20'], line=dict(color='yellow', width=1), name="EMA 20"))
fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df['Support'], line=dict(color='green', dash='dash'), name="Support"))
fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df['Resistance'], line=dict(color='red', dash='dash'), name="Resistance"))

fig.update_layout(height=600, template="plotly_dark", xaxis_rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True)

st.info("💡 Tip: Use the 'View Chart' dropdown above to switch between different stocks in the sector.")
