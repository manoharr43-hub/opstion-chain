import streamlit as st
import yfinance as yf
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# =============================
# CONFIG
# =============================
st.set_page_config(page_title="🔥 ULTIMATE NSE AI SCANNER", layout="wide")
st_autorefresh(interval=60000, key="refresh") 

st.title("🚀 ULTIMATE NSE AI SCANNER")
st.markdown("---")

# =============================
# LOGIC FUNCTIONS
# =============================
def get_stock_analysis(ticker_symbol):
    try:
        t = yf.Ticker(ticker_symbol)
        # Fetching data for different timeframes
        df_5m = t.history(period="1d", interval="5m")
        df_15m = t.history(period="5d", interval="15m")
        df_1h = t.history(period="1mo", interval="1h")

        if df_15m.empty or len(df_15m) < 20:
            return None

        # 1. Trend Analysis (EMA 20/50)
        def check_trend(df):
            ema20 = df['Close'].ewm(span=20).mean().iloc[-1]
            ema50 = df['Close'].ewm(span=50).mean().iloc[-1]
            return "UP" if ema20 > ema50 else "DOWN"

        t5 = check_trend(df_5m)
        t15 = check_trend(df_15m)
        t1h = check_trend(df_1h)

        # 2. Big Players Activity (Volume Analysis)
        avg_vol = df_15m['Volume'].mean()
        curr_vol = df_15m['Volume'].iloc[-1]
        big_player = "🔥 ACTIVE" if curr_vol > avg_vol * 1.5 else "💤 NORMAL"

        # 3. Entry, SL, Target Logic
        curr_price = df_15m['Close'].iloc[-1]
        high_24h = df_15m['High'].max()
        low_24h = df_15m['Low'].min()
        atr = (high_24h - low_24h) * 0.2  # Basic ATR alternative

        if t15 == "UP":
            signal = "🟢 BUY"
            entry = curr_price
            sl = curr_price - atr
            target = curr_price + (atr * 2)
        else:
            signal = "🔴 SELL"
            entry = curr_price
            sl = curr_price + atr
            target = curr_price - (atr * 2)

        # 4. Strength Logic
        strength = "WAIT"
        if t5 == "UP" and t15 == "UP" and t1h == "UP":
            strength = "🚀 STRONG BUY"
        elif t5 == "DOWN" and t15 == "DOWN" and t1h == "DOWN":
            strength = "💀 STRONG SELL"

        return {
            "Stock": ticker_symbol.replace(".NS", ""),
            "Price": round(curr_price, 2),
            "Signal": signal,
            "Strength": strength,
            "Big Players": big_player,
            "Entry": round(entry, 2),
            "StopLoss": round(sl, 2),
            "Target": round(target, 2)
        }
    except:
        return None

# =============================
# SECTORS LIST (More Sectors Added)
# =============================
sectors = {
    "Nifty 50": ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS","SBIN.NS","BHARTIARTL.NS","LT.NS","ITC.NS","AXISBANK.NS"],
    "Banking & Finance": ["HDFCBANK.NS","ICICIBANK.NS","SBIN.NS","AXISBANK.NS","KOTAKBANK.NS","BAJFINANCE.NS","CHOLAFIN.NS"],
    "IT Sector": ["TCS.NS","INFY.NS","WIPRO.NS","HCLTECH.NS","TECHM.NS","LTIM.NS"],
    "Auto & Motors": ["TATAMOTORS.NS","MARUTI.NS","M&M.NS","HEROMOTOCO.NS","EICHERMOT.NS","ASHOKLEY.NS"],
    "Energy & Pharma": ["RELIANCE.NS","NTPC.NS","POWERGRID.NS","SUNPHARMA.NS","DRREDDY.NS","CIPLA.NS"],
    "Metal & Infra": ["TATASTEEL.NS","JINDALSTEL.NS","HINDALCO.NS","ADANIENT.NS","ADANIPORTS.NS"]
}

selected_sector = st.selectbox("📂 Select Sector to Scan", list(sectors.keys()))
stocks = sectors[selected_sector]

if st.button("🔍 START SCANNER"):
    with st.spinner(f"Analyzing {len(stocks)} stocks in {selected_sector}..."):
        all_results = []
        for s in stocks:
            res = get_stock_analysis(s)
            if res:
                all_results.append(res)
        
        if all_results:
            df = pd.DataFrame(all_results)
            
            # Display Main Table
            st.subheader(f"📊 {selected_sector} Analysis Results")
            st.dataframe(df, use_container_width=True)

            # =============================
            # MARKET SUMMARY (Bottom Section)
            # =============================
            st.markdown("---")
            st.subheader("🏁 Sector Market Summary")
            
            col1, col2, col3 = st.columns(3)
            
            strong_buys = len(df[df['Strength'] == "🚀 STRONG BUY"])
            strong_sells = len(df[df['Strength'] == "💀 STRONG SELL"])
            active_big_players = len(df[df['Big Players'] == "🔥 ACTIVE"])

            col1.metric("🚀 Strong Buy Stocks", strong_buys)
            col2.metric("💀 Strong Sell Stocks", strong_sells)
            col3.metric("🔥 Big Player Activity", active_big_players)
            
            if strong_buys > strong_sells:
                st.success(f"💡 Market Tip: {selected_sector} is looking BULLISH. Focus on Strong Buy stocks with High Volume.")
            elif strong_sells > strong_buys:
                st.error(f"💡 Market Tip: {selected_sector} is looking BEARISH. Be careful with long positions.")
            else:
                st.warning("💡 Market Tip: Sector is Neutral. Wait for a clear trend.")
        else:
            st.error("No data found. Check your internet or API limits.")
