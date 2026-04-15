import streamlit as st
import yfinance as yf
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# =============================
# CONFIG
# =============================
st.set_page_config(page_title="🔥 PRO NSE AI DASHBOARD", layout="wide")
st_autorefresh(interval=15000, key="refresh")

st.title("🔥 PRO NSE AI DASHBOARD + SCANNER (SAFE FINAL)")
st.markdown("---")

# =============================
# TABS
# =============================
tab1, tab2 = st.tabs(["📊 Dashboard", "🔥 Scanner"])

# =============================
# SAFE DATA LOAD
# =============================
@st.cache_data(ttl=60)
def get_data(symbol):
    try:
        df = yf.download(symbol, period="3mo", interval="1d", progress=False)
        if df is None or df.empty:
            return None
        return df
    except:
        return None

@st.cache_data(ttl=60)
def get_multi_data(tickers):
    try:
        data = yf.download(
            tickers,
            period="15d",
            interval="15m",
            group_by="ticker",
            progress=False
        )
        if data is None or len(data) == 0:
            return None
        return data
    except:
        return None

# =============================
# 📊 DASHBOARD
# =============================
with tab1:
    st.subheader("📊 Simple Dashboard")

    stock = st.text_input("Enter Stock (Example: RELIANCE)", "RELIANCE")

    if not stock.endswith(".NS"):
        stock = stock + ".NS"

    df = get_data(stock)

    if df is not None and not df.empty:

        st.line_chart(df['Close'])

        df['SMA20'] = df['Close'].rolling(20).mean()
        df['SMA50'] = df['Close'].rolling(50).mean()

        col1, col2 = st.columns(2)

        price = df['Close'].iloc[-1]
        col1.metric("Price", round(price, 2))

        sma20 = df['SMA20'].dropna()
        sma50 = df['SMA50'].dropna()

        if len(sma20) > 0 and len(sma50) > 0:
            trend = "UP" if sma20.iloc[-1] > sma50.iloc[-1] else "DOWN"
        else:
            trend = "N/A"

        col2.metric("Trend", trend)

    else:
        st.error("❌ Data Not Loading")

# =============================
# 🔥 SCANNER
# =============================
with tab2:
    st.subheader("🔥 NSE MULTI SECTOR SCANNER (FINAL SAFE)")

    sectors = {
        "Nifty 50": ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS"],
        "Banking": ["SBIN.NS","AXISBANK.NS","KOTAKBANK.NS","PNB.NS"],
        "IT": ["WIPRO.NS","HCLTECH.NS","TECHM.NS"],
        "Auto": ["MARUTI.NS","TATAMOTORS.NS","M&M.NS"],
        "FMCG": ["HINDUNILVR.NS","ITC.NS","NESTLEIND.NS"],
        "Pharma": ["SUNPHARMA.NS","DRREDDY.NS","CIPLA.NS"],
        "Energy": ["ONGC.NS","IOC.NS","BPCL.NS"],
        "Metal": ["TATASTEEL.NS","JSWSTEEL.NS","HINDALCO.NS"],
        "Finance": ["BAJFINANCE.NS","BAJAJFINSV.NS","SHRIRAMFIN.NS"]
    }

    sector = st.selectbox("Select Sector", list(sectors.keys()))
    stocks = sectors[sector][:3]

    data = get_multi_data(stocks)

    results = []

    if data is not None:

        for stock in stocks:
            try:

                if stock not in data.columns.get_level_values(0):
                    continue

                df = data[stock].dropna()

                if df is None or df.empty or len(df) < 30:
                    continue

                # =============================
                # INDICATORS
                # =============================
                df['EMA20'] = df['Close'].ewm(span=20).mean()
                df['EMA50'] = df['Close'].ewm(span=50).mean()

                price = df['Close'].iloc[-1]
                ema20 = df['EMA20'].iloc[-1]
                ema50 = df['EMA50'].iloc[-1]

                # =============================
                # SIGNAL LOGIC (FIXED)
                # =============================
                if ema20 > ema50 and price > ema20:
                    signal = "🟢 BUY"
                elif ema20 < ema50 and price < ema20:
                    signal = "🔴 SELL"
                else:
                    signal = "🟡 NO TRADE"

                prev = df.iloc[-2]

                if signal == "🟢 BUY":
                    entry = prev['High']
                    sl = prev['Low']
                    target = entry + (entry - sl) * 1.5

                elif signal == "🔴 SELL":
                    entry = prev['Low']
                    sl = prev['High']
                    target = entry - (sl - entry) * 1.5

                else:
                    entry = price
                    sl = price
                    target = price

                # =============================
                # 5M TREND (SAFE)
                # =============================
                try:
                    df5 = yf.download(stock, period="5d", interval="5m", progress=False)
                    if df5 is not None and len(df5) > 20:
                        df5['EMA20'] = df5['Close'].ewm(span=20).mean()
                        df5['EMA50'] = df5['Close'].ewm(span=50).mean()
                        t5 = "UP" if df5['EMA20'].iloc[-1] > df5['EMA50'].iloc[-1] else "DOWN"
                    else:
                        t5 = "N/A"
                except:
                    t5 = "N/A"

                # =============================
                # 15M TREND (SAFE)
                # =============================
                try:
                    df15 = yf.download(stock, period="5d", interval="15m", progress=False)
                    if df15 is not None and len(df15) > 20:
                        df15['EMA20'] = df15['Close'].ewm(span=20).mean()
                        df15['EMA50'] = df15['Close'].ewm(span=50).mean()
                        t15 = "UP" if df15['EMA20'].iloc[-1] > df15['EMA50'].iloc[-1] else "DOWN"
                    else:
                        t15 = "N/A"
                except:
                    t15 = "N/A"

                results.append({
                    "Stock": stock,
                    "Signal": signal,
                    "Price": round(price,2),
                    "Entry": round(entry,2),
                    "SL": round(sl,2),
                    "Target": round(target,2),
                    "5M Trend": t5,
                    "15M Trend": t15
                })

            except:
                continue

    df_res = pd.DataFrame(results)

    if df_res.empty:
        st.warning("⚠️ No Data Found")
    else:
        st.dataframe(df_res, use_container_width=True)

        st.subheader("📊 Detail View")

        s = st.selectbox("Select Stock", df_res["Stock"])
        row = df_res[df_res["Stock"] == s].iloc[0]

        c1, c2 = st.columns(2)
        c1.metric("5M Trend", row["5M Trend"])
        c2.metric("15M Trend", row["15M Trend"])

        st.subheader("📈 Chart")
        st.line_chart(data[s]["Close"].resample("1D").last())
