import streamlit as st
import yfinance as yf
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# =============================
# CONFIG
# =============================
st.set_page_config(page_title="🔥 PRO NSE AI DASHBOARD", layout="wide")
st_autorefresh(interval=30000, key="refresh") 

st.title("🔥 PRO NSE AI DASHBOARD")
st.markdown("---")

tab1, tab2 = st.tabs(["📊 Individual Analysis", "🔥 Multi-Timeframe Scanner"])

# =============================
# FUNCTIONS
# =============================
@st.cache_data(ttl=60)
def get_trend(df):
    if df is None or len(df) < 50:
        return "N/A"
    ema20 = df['Close'].ewm(span=20).mean().iloc[-1]
    ema50 = df['Close'].ewm(span=50).mean().iloc[-1]
    return "🟢 BULLISH" if ema20 > ema50 else "🔴 BEARISH"

# =============================
# 📊 TAB 1: DASHBOARD
# =============================
with tab1:
    stock = st.text_input("Enter Stock", "RELIANCE").upper()
    if not stock.endswith(".NS"): stock += ".NS"
    
    df_dash = yf.download(stock, period="5d", interval="15m", progress=False)
    if not df_dash.empty:
        st.line_chart(df_dash['Close'])
        st.metric("Price", round(df_dash['Close'].iloc[-1], 2))

# =============================
# 🔥 TAB 2: MULTI-TIMEFRAME SCANNER
# =============================
with tab2:
    sectors = {
        "Nifty 50": ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS","SBIN.NS"],
        "Banking": ["SBIN.NS","AXISBANK.NS","KOTAKBANK.NS","ICICIBANK.NS","HDFCBANK.NS"],
        "Auto": ["MARUTI.NS","TATAMOTORS.NS","M&M.NS","HEROMOTOCO.NS"]
    }
    
    selected_sector = st.selectbox("Select Sector", list(sectors.keys()))
    stocks = sectors[selected_sector]

    if st.button("Run Scanner"):
        with st.spinner("Scanning..."):
            results = []
            
            # ఒక్కొక్కటిగా డేటా తీసుకోవడం వల్ల ఎర్రర్స్ తగ్గుతాయి
            for s in stocks:
                try:
                    d5 = yf.download(s, period="2d", interval="5m", progress=False)
                    d15 = yf.download(s, period="5d", interval="15m", progress=False)
                    d1h = yf.download(s, period="1mo", interval="1h", progress=False)
                    
                    t5 = get_trend(d5)
                    t15 = get_trend(d15)
                    t1h = get_trend(d1h)
                    
                    price = d15['Close'].iloc[-1]
                    
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
                # ఇక్కడ నేరుగా టేబుల్ చూపిస్తున్నాము, ఎర్రర్ రాకుండా స్టైలింగ్ తీసేశాను
                st.dataframe(df_res, use_container_width=True)
            else:
                st.warning("No Data Found")
