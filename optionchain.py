import streamlit as st
import yfinance as yf
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# =============================
# CONFIG
# =============================
st.set_page_config(page_title="🔥 PRO NSE AI DASHBOARD", layout="wide")
st_autorefresh(interval=30000, key="refresh") # 30 Sec refresh to avoid rate limits

st.title("🔥 PRO NSE AI DASHBOARD (Multi-Timeframe)")
st.markdown("---")

tab1, tab2 = st.tabs(["📊 Individual Analysis", "🔥 Multi-Timeframe Scanner"])

# =============================
# DATA LOADER FUNCTIONS
# =============================
@st.cache_data(ttl=60)
def get_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="5d", interval="15m")
        return df if not df.empty else None
    except:
        return None

def get_trend(df):
    """EMA 20 vs EMA 50 ఆధారంగా ట్రెండ్ లెక్కిస్తుంది"""
    if df is None or len(df) < 50:
        return "N/A"
    ema20 = df['Close'].ewm(span=20).mean().iloc[-1]
    ema50 = df['Close'].ewm(span=50).mean().iloc[-1]
    return "🟢 BULLISH" if ema20 > ema50 else "🔴 BEARISH"

@st.cache_data(ttl=60)
def get_scanner_data(tickers):
    """అన్ని టైమ్ ఫ్రేమ్స్ డేటాను ఒకేసారి తెస్తుంది"""
    try:
        # 5min, 15m, 1h డేటా కోసం 
        data_5m = yf.download(tickers, period="2d", interval="5m", group_by='ticker', progress=False)
        data_15m = yf.download(tickers, period="5d", interval="15m", group_by='ticker', progress=False)
        data_1h = yf.download(tickers, period="1mo", interval="1h", group_by='ticker', progress=False)
        return data_5m, data_15m, data_1h
    except:
        return None, None, None

# =============================
# 📊 TAB 1: DASHBOARD
# =============================
with tab1:
    st.subheader("📊 Quick Chart Analysis")
    stock = st.text_input("Enter Stock", "RELIANCE").upper()
    if not stock.endswith(".NS"): stock += ".NS"

    df_dash = get_data(stock)
    if df_dash is not None:
        st.line_chart(df_dash['Close'])
        st.metric("Current Price", round(df_dash['Close'].iloc[-1], 2))
    else:
        st.error("Data Not Found")

# =============================
# 🔥 TAB 2: MULTI-TIMEFRAME SCANNER
# =============================
with tab2:
    st.subheader("🔥 Smart Multi-Timeframe Scanner")
    
    sectors = {
        "Nifty 50": ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS","SBIN.NS","BHARTIARTL.NS"],
        "Banking": ["SBIN.NS","AXISBANK.NS","KOTAKBANK.NS","ICICIBANK.NS","HDFCBANK.NS"],
        "Auto": ["MARUTI.NS","TATAMOTORS.NS","M&M.NS","HEROMOTOCO.NS"]
    }
    
    selected_sector = st.selectbox("Select Sector", list(sectors.keys()))
    stocks = sectors[selected_sector]

    if st.button("Run Scanner"):
        with st.spinner("Scanning 5m, 15m, and 1h Trends..."):
            d5, d15, d1h = get_scanner_data(stocks)
            
            results = []
            for s in stocks:
                try:
                    # ట్రెండ్స్ లెక్కించడం
                    t5 = get_trend(d5[s].dropna())
                    t15 = get_trend(d15[s].dropna())
                    t1h = get_trend(d1h[s].dropna())
                    
                    price = d15[s]['Close'].dropna().iloc[-1]
                    
                    # Recommendation logic
                    action = "WAIT"
                    if t5 == "🟢 BULLISH" and t15 == "🟢 BULLISH" and t1h == "🟢 BULLISH":
                        action = "🚀 STRONG BUY"
                    elif t5 == "🔴 BEARISH" and t15 == "🔴 BEARISH" and t1h == "🔴 BEARISH":
                        action = "💀 STRONG SELL"
                    
                    results.append({
                        "Stock": s,
                        "Price": round(price, 2),
                        "5 Min": t5,
                        "15 Min": t15,
                        "1 Hour": t1h,
                        "Signal": action
                    })
                except:
                    continue
            
            if results:
                df_res = pd.DataFrame(results)
                
                # స్టైలింగ్ - సిగ్నల్ ని బట్టి రంగులు మార్చడం
                def color_signal(val):
                    color = 'green' if 'BUY' in val else 'red' if 'SELL' in val else 'white'
                    return f'color: {color}'

                st.dataframe(df_res.style.applymap(color_signal, subset=['Signal']), use_container_width=True)
                
                st.success("💡 సూచన: మూడు టైమ్ ఫ్రేమ్స్ (5m, 15m, 1h) ఒకే ట్రెండ్ చూపిస్తే ఆ ట్రేడ్ సక్సెస్ అయ్యే అవకాశం ఎక్కువ ఉంటుంది.")
            else:
                st.warning("No data found for the selected stocks.")
