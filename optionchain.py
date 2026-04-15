import streamlit as st
import yfinance as yf
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# =============================
# CONFIG
# =============================
st.set_page_config(page_title="🔥 PRO NSE AI DASHBOARD", layout="wide")
st_autorefresh(interval=60000, key="refresh") # 1 minute refresh to stay safe

st.title("🔥 PRO NSE AI DASHBOARD")
st.markdown("---")

tab1, tab2 = st.tabs(["📊 Individual Analysis", "🔥 Multi-Timeframe Scanner"])

# =============================
# TREND CALCULATOR
# =============================
def get_trend_status(ticker_symbol, timeframe, period):
    try:
        t = yf.Ticker(ticker_symbol)
        df = t.history(period=period, interval=timeframe)
        if df.empty or len(df) < 10:
            return "N/A", 0
        
        # EMA Calculations
        ema20 = df['Close'].ewm(span=20).mean().iloc[-1]
        ema50 = df['Close'].ewm(span=50).mean().iloc[-1]
        current_price = df['Close'].iloc[-1]
        
        status = "🟢 BULLISH" if ema20 > ema50 else "🔴 BEARISH"
        return status, current_price
    except:
        return "N/A", 0

# =============================
# 📊 TAB 1: DASHBOARD
# =============================
with tab1:
    stock = st.text_input("Enter Stock", "RELIANCE").upper()
    if not stock.endswith(".NS"): stock += ".NS"
    
    t_dash = yf.Ticker(stock)
    df_dash = t_dash.history(period="5d", interval="15m")
    if not df_dash.empty:
        st.line_chart(df_dash['Close'])
        st.metric("Current Price", round(df_dash['Close'].iloc[-1], 2))

# =============================
# 🔥 TAB 2: MULTI-TIMEFRAME SCANNER
# =============================
with tab2:
    sectors = {
        "Nifty 50": ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS","SBIN.NS","BHARTIARTL.NS","LT.NS"],
        "Banking": ["SBIN.NS","AXISBANK.NS","KOTAKBANK.NS","ICICIBANK.NS","HDFCBANK.NS","INDUSINDBK.NS"],
        "Auto": ["MARUTI.NS","TATAMOTORS.NS","M&M.NS","HEROMOTOCO.NS","EICHERMOT.NS"]
    }
    
    selected_sector = st.selectbox("Select Sector", list(sectors.keys()))
    stocks = sectors[selected_sector]

    if st.button("Run Scanner"):
        with st.spinner(f"Scanning {len(stocks)} stocks... Please wait."):
            results = []
            
            for s in stocks:
                # 5 Min Trend
                t5, price = get_trend_status(s, "5m", "1d")
                # 15 Min Trend
                t15, _ = get_trend_status(s, "15m", "5d")
                # 1 Hour Trend
                t1h, _ = get_trend_status(s, "1h", "1mo")
                
                if t15 != "N/A":
                    # Signal Logic
                    action = "WAIT"
                    if t5 == "🟢 BULLISH" and t15 == "🟢 BULLISH" and t1h == "🟢 BULLISH":
                        action = "🚀 STRONG BUY"
                    elif t5 == "🔴 BEARISH" and t15 == "🔴 BEARISH" and t1h == "🔴 BEARISH":
                        action = "💀 STRONG SELL"
                    
                    results.append({
                        "Stock": s.replace(".NS", ""),
                        "Price": round(price, 2),
                        "5 Min": t5,
                        "15 Min": t15,
                        "1 Hour": t1h,
                        "Signal": action
                    })
            
            if results:
                df_res = pd.DataFrame(results)
                # Displaying the dataframe
                st.dataframe(df_res, use_container_width=True)
            else:
                st.error("⚠️ No data could be fetched. Please try again in a few seconds.")
