import streamlit as st
import yfinance as yf
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# =============================
# CONFIG
# =============================
st.set_page_config(page_title="🔥 PRO NSE AI DASHBOARD ULTIMATE", layout="wide")
st_autorefresh(interval=15000, key="refresh")

st.title("🔥 PRO NSE AI DASHBOARD + MULTI TF SCANNER")
st.markdown("---")

# =============================
# TABS
# =============================
tab1, tab2 = st.tabs(["📊 Dashboard", "🔥 Scanner"])

# =============================
# DATA FUNCTION
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
        return yf.download(
            tickers,
            period="15d",
            interval="15m",
            group_by="ticker",
            progress=False
        )
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
    st.subheader("🔥 NSE MULTI-SECTOR SCANNER")

    # =============================
    # ➕ EXPANDED SECTORS
    # =============================
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
                df = data[stock].dropna()

                if len(df) < 30:
                    continue

                # =============================
                # EMA STRATEGY
                # =============================
                df['EMA20'] = df['Close'].ewm(span=20).mean()
                df['EMA50'] = df['Close'].ewm(span=50).mean()

                signal = "🟢 BUY" if df['EMA20'].iloc[-1] > df['EMA50'].iloc[-1] else "🔴 SELL"

                price = df['Close'].iloc[-1]
                prev = df.iloc[-2]

                if "BUY" in signal:
                    entry = prev['High']
                    sl = prev['Low']
                    target = entry + (entry - sl) * 1.5
                else:
                    entry = prev['Low']
                    sl = prev['High']
                    target = entry - (sl - entry) * 1.5

                # =============================
                # 5M / 15M TREND
                # =============================
                t5 = "UP" if df['EMA20'].iloc[-1] > df['EMA50'].iloc[-1] else "DOWN"

                # =============================
                # 2M TIMEFRAME (NEW)
                # =============================
                try:
                    df_2m = yf.download(stock, period="5d", interval="2m", progress=False)
                    if df_2m is not None and not df_2m.empty:
                        df_2m['EMA20'] = df_2m['Close'].ewm(span=20).mean()
                        df_2m['EMA50'] = df_2m['Close'].ewm(span=50).mean()
                        t2m = "UP" if df_2m['EMA20'].iloc[-1] > df_2m['EMA50'].iloc[-1] else "DOWN"
                    else:
                        t2m = "N/A"
                except:
                    t2m = "N/A"

                # =============================
                # 1H TIMEFRAME (SAFE FIX)
                # =============================
                try:
                    df1h = df.resample("1h").last().dropna()

                    if len(df1h) > 20:
                        sma1h = df1h['Close'].rolling(20).mean().dropna()
                        if len(sma1h) > 0:
                            t1h = "UP" if df1h['Close'].iloc[-1] > sma1h.iloc[-1] else "DOWN"
                        else:
                            t1h = "N/A"
                    else:
                        t1h = "N/A"
                except:
                    t1h = "N/A"

                results.append({
                    "Stock": stock,
                    "Signal": signal,
                    "Price": round(price, 2),
                    "Entry": round(entry, 2),
                    "SL": round(sl, 2),
                    "Target": round(target, 2),
                    "2M": t2m,
                    "15M": t5,
                    "1H": t1h
                })

            except:
                continue

    df_res = pd.DataFrame(results)

    if df_res.empty:
        st.warning("⚠️ No Data Found")
    else:
        st.dataframe(df_res, use_container_width=True)

        st.subheader("📦 Multi Timeframe View")

        s = st.selectbox("Select Stock", df_res["Stock"])
        row = df_res[df_res["Stock"] == s].iloc[0]

        c1, c2, c3 = st.columns(3)
        c1.metric("2M Trend", row["2M"])
        c2.metric("15M Trend", row["15M"])
        c3.metric("1H Trend", row["1H"])

        st.subheader("📈 Chart (Daily)")
        st.line_chart(data[s]["Close"].resample("1D").last())
