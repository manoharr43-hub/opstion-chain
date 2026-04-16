import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# =============================
# 1. CONFIG
# =============================
st.set_page_config(page_title="🔥 MANOHAR NSE AI PRO", layout="wide")
st_autorefresh(interval=60000, key="refresh")

st.title("🚀 MANOHAR NSE AI PRO TERMINAL")
st.markdown("---")

# =============================
# 2. SAFE VALUE
# =============================
def get_value(x):
    if isinstance(x, pd.Series):
        return float(x.iloc[0])
    return float(x)

# =============================
# 3. ANALYSIS LOGIC (UNCHANGED CORE)
# =============================
def analyze_data(df):
    if df is None or len(df) < 20:
        return None

    e20 = df['Close'].ewm(span=20).mean()
    e50 = df['Close'].ewm(span=50).mean()

    vol = df['Volume']
    avg_vol = vol.rolling(window=20).mean()

    curr_price = get_value(df['Close'].iloc[-1])
    curr_e20 = get_value(e20.iloc[-1])
    curr_e50 = get_value(e50.iloc[-1])
    curr_vol = get_value(vol.iloc[-1])
    curr_avg_vol = get_value(avg_vol.iloc[-1])

    if pd.isna(curr_avg_vol) or curr_avg_vol == 0:
        return None

    cp_strength = "🔵 CALL STRONG" if curr_e20 > curr_e50 else "🔴 PUT STRONG"

    if curr_vol > curr_avg_vol * 2:
        big_player = "🔥 EXTREME INSTITUTIONAL"
    elif curr_vol > curr_avg_vol * 1.5:
        big_player = "🐋 BIG PLAYER ACTIVE"
    else:
        big_player = "💤 NORMAL"

    observation = "WAIT"
    entry, sl, target = 0, 0, 0

    recent_high = df['High'].iloc[-10:].max()
    recent_low = df['Low'].iloc[-10:].min()
    risk = (recent_high - recent_low) if (recent_high - recent_low) > 0 else curr_price * 0.01

    # 🔥 Balanced Logic
    trend_strength = abs(curr_e20 - curr_e50)
    price_momentum = df['Close'].iloc[-1] - df['Close'].iloc[-3]

    if (
        curr_e20 > curr_e50 and
        curr_vol > curr_avg_vol * 0.5 and
        trend_strength > curr_price * 0.001 and
        price_momentum > 0
    ):
        observation = "🚀 STRONG BUY"
        entry = curr_price
        sl = curr_price - (risk * 0.5)
        target = curr_price + risk

    elif (
        curr_e20 < curr_e50 and
        curr_vol > curr_avg_vol * 0.5 and
        trend_strength > curr_price * 0.001 and
        price_momentum < 0
    ):
        observation = "💀 STRONG SELL"
        entry = curr_price
        sl = curr_price + (risk * 0.5)
        target = curr_price - risk

    # 🔥 fallback (important)
    if observation == "WAIT":
        if curr_e20 > curr_e50:
            observation = "⚡ WEAK BUY"
        else:
            observation = "⚡ WEAK SELL"

    return (
        cp_strength,
        observation,
        big_player,
        round(entry, 2),
        round(sl, 2),
        round(target, 2)
    )

# =============================
# 4. NSE SECTORS
# =============================
all_sectors = {
    "Nifty 50": ["RELIANCE","TCS","INFY","HDFCBANK","ICICIBANK","SBIN","ITC","LT","AXISBANK","BHARTIARTL"],
    "Banking": ["SBIN","AXISBANK","KOTAKBANK","HDFCBANK","ICICIBANK","PNB","CANBK","FEDERALBNK"],
    "IT": ["TCS","INFY","WIPRO","HCLTECH"],
    "Auto": ["TATAMOTORS","MARUTI","M&M"]
}

# =============================
# 5. SIDEBAR
# =============================
st.sidebar.title("📂 Backtest Panel")
bt_date = st.sidebar.date_input("Select Date", datetime.now() - timedelta(days=1))
bt_stock_input = st.sidebar.text_input("Stock (optional)", "").upper()

# =============================
# 6. MAIN SCANNER
# =============================
selected_sector = st.selectbox("📂 Select Sector", list(all_sectors.keys()))
stocks = all_sectors[selected_sector]

if st.button("🔍 START LIVE SCANNER", use_container_width=True):

    results = []

    with st.spinner("Scanning..."):
        for s in stocks:
            try:
                df = yf.download(s + ".NS", period="5d", interval="15m", progress=False)

                if df.empty:
                    continue

                df.columns = df.columns.get_level_values(0)

                res = analyze_data(df)

                if res:
                    results.append({
                        "Stock": s,
                        "Signal": res[1],
                        "Price": get_value(df['Close'].iloc[-1])
                    })

            except:
                continue

    if results:
        st.dataframe(pd.DataFrame(results), use_container_width=True)
    else:
        st.error("No Signals Found")

# =============================
# 7. BACKTEST (FIXED)
# =============================
st.markdown("---")
st.subheader(f"📅 Backtest Report - {bt_date}")

if st.sidebar.button("📊 RUN BACKTEST"):

    bt_results = []
    target_list = [bt_stock_input] if bt_stock_input else stocks

    with st.spinner("Running Backtest..."):

        for s in target_list:
            try:
                df_hist = yf.download(s + ".NS", period="5d", interval="15m", progress=False)

                if df_hist.empty:
                    continue

                df_hist.columns = df_hist.columns.get_level_values(0)

                df_hist = df_hist[df_hist.index.date == bt_date]
                df_hist = df_hist.between_time("09:15", "15:30")

                if len(df_hist) < 20:
                    continue

                for i in range(20, len(df_hist)):
                    sub_df = df_hist.iloc[:i+1]
                    res = analyze_data(sub_df)

                    # 🔥 FIXED (NO FILTER)
                    if res:
                        bt_results.append({
                            "Time": sub_df.index[-1].strftime('%H:%M'),
                            "Stock": s,
                            "Signal": res[1],
                            "Entry": res[3],
                            "SL": res[4],
                            "Target": res[5]
                        })

            except:
                continue

    if bt_results:
        st.dataframe(pd.DataFrame(bt_results), use_container_width=True)
    else:
        st.warning("No Signals Found")
