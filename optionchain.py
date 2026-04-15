import streamlit as st
import yfinance as yf
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# =============================
# 1. CONFIG & REFRESH
# =============================
st.set_page_config(page_title="🔥 MANOHAR NSE AI PRO", layout="wide")
st_autorefresh(interval=60000, key="refresh") 

st.title("🚀 MANOHAR NSE AI PRO DASHBOARD")
st.markdown("---")

# =============================
# 2. OPTION CHAIN ANALYSIS (NEW)
# =============================
def get_option_data(symbol):
    try:
        t = yf.Ticker(symbol)
        if not t.options:
            return "⚖️ NEUTRAL", 0.0
        
        # ఇమ్మీడియట్ ఎక్స్‌పైరీ డేటా
        expiry = t.options[0]
        opt = t.option_chain(expiry)
        
        call_vol = opt.calls['volume'].sum()
        put_vol = opt.puts['volume'].sum()
        
        if call_vol == 0: return "⚖️ NEUTRAL", 0.0
        
        pcr = put_vol / call_vol
        
        # Logic for Call/Put Strength
        if pcr < 0.7:
            strength = "🔵 CALL SIDE STRONG"
        elif pcr > 1.3:
            strength = "🔴 PUT SIDE STRONG"
        else:
            strength = "⚖️ NEUTRAL"
            
        return strength, round(pcr, 2)
    except:
        return "N/A", 0.0

# =============================
# 3. CORE ANALYSIS ENGINE
# =============================
def get_detailed_analysis(symbol):
    try:
        t = yf.Ticker(symbol)
        df_5m = t.history(period="1d", interval="5m")
        df_15m = t.history(period="5d", interval="15m")
        df_1h = t.history(period="1mo", interval="1h")

        if df_15m.empty or len(df_15m) < 20: return None

        # --- Trend Logic (EMA 20 vs 50) ---
        def calc_trend(df):
            e20 = df['Close'].ewm(span=20).mean().iloc[-1]
            e50 = df['Close'].ewm(span=50).mean().iloc[-1]
            return "UP" if e20 > e50 else "DOWN"

        t5, t15, t1h = calc_trend(df_5m), calc_trend(df_15m), calc_trend(df_1h)
        
        # --- Big Players (Volume Spike) ---
        avg_vol = df_15m['Volume'].mean()
        last_vol = df_15m['Volume'].iloc[-1]
        big_player = "🔥 ACTIVE" if last_vol > (avg_vol * 1.8) else "💤 NORMAL"

        # --- Option Strength (NEW) ---
        opt_obs, pcr_val = get_option_data(symbol)

        # --- Price Metrics ---
        cp = df_15m['Close'].iloc[-1]
        high, low = df_15m['High'].iloc[-5:].max(), df_15m['Low'].iloc[-5:].min()
        range_val = max(high - low, cp * 0.01)

        # --- Entry, SL, Target Calculation ---
        if t15 == "UP":
            signal, entry = "🟢 BUY", high + (range_val * 0.1)
            sl = low - (range_val * 0.2)
            target = entry + (entry - sl) * 1.5
        else:
            signal, entry = "🔴 SELL", low - (range_val * 0.1)
            sl = high + (range_val * 0.2)
            target = entry - (sl - entry) * 1.5

        # --- Strength Logic (Observation) ---
        strength = "WAIT"
        if t5 == "UP" and t15 == "UP" and t1h == "UP": strength = "🚀 STRONG BUY"
        elif t5 == "DOWN" and t15 == "DOWN" and t1h == "DOWN": strength = "💀 STRONG SELL"

        return {
            "Stock": symbol.replace(".NS", ""),
            "Price": round(cp, 2),
            "Signal": signal,
            "Observation": strength,
            "Option Strength": opt_obs,
            "PCR": pcr_val,
            "Big Players": big_player,
            "Entry": round(entry, 2),
            "StopLoss": round(sl, 2),
            "Target": round(target, 2)
        }
    except: return None

# =============================
# 4. SECTOR SELECTION
# =============================
sectors = {
    "Nifty 50": ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS","SBIN.NS","ITC.NS","LT.NS","AXISBANK.NS","BHARTIARTL.NS"],
    "Banking": ["SBIN.NS","AXISBANK.NS","KOTAKBANK.NS","HDFCBANK.NS","ICICIBANK.NS","BAJFINANCE.NS","PNB.NS","CANBK.NS"],
    "IT": ["TCS.NS","INFY.NS","WIPRO.NS","HCLTECH.NS","TECHM.NS","LTIM.NS","COFORGE.NS"],
    "Auto": ["TATAMOTORS.NS","MARUTI.NS","M&M.NS","HEROMOTOCO.NS","EICHERMOT.NS","ASHOKLEY.NS","TVSMOTOR.NS"],
    "Pharma": ["SUNPHARMA.NS","DRREDDY.NS","CIPLA.NS","APOLLOHOSP.NS","DIVISLAB.NS"],
    "Energy": ["NTPC.NS","POWERGRID.NS","ONGC.NS","BPCL.NS","TATAPOWER.NS","ADANIGREEN.NS"]
}

selected_sector = st.selectbox("📂 Select Market Sector", list(sectors.keys()))

if st.button("🔍 START SCANNER", use_container_width=True):
    with st.spinner("AI analyzing Trends & Option Chain..."):
        results = [res for s in sectors[selected_sector] if (res := get_detailed_analysis(s))]
        
        if results:
            df = pd.DataFrame(results)
            st.subheader(f"📊 {selected_sector} Live Signals")
            st.dataframe(df, use_container_width=True)

            # --- BOTTOM SUMMARY SECTION ---
            st.markdown("---")
            st.subheader("🏁 NSE Trend & Option Summary")
            
            s_buy_list = df[df['Observation'] == "🚀 STRONG BUY"]["Stock"].tolist()
            s_sell_list = df[df['Observation'] == "💀 STRONG SELL"]["Stock"].tolist()
            call_strong_list = df[df['Option Strength'] == "🔵 CALL SIDE STRONG"]["Stock"].tolist()
            put_strong_list = df[df['Option Strength'] == "🔴 PUT SIDE STRONG"]["Stock"].tolist()

            col1, col2 = st.columns(2)

            with col1:
                st.success(f"📈 **BULLISH ZONE (Call Strong)**")
                if call_strong_list:
                    for s in call_strong_list: st.write(f"✅ {s} (PCR: {df[df['Stock']==s]['PCR'].values[0]})")
                else: st.write("None")

            with col2:
                st.error(f"📉 **BEARISH ZONE (Put Strong)**")
                if put_strong_list:
                    for s in put_strong_list: st.write(f"❌ {s} (PCR: {df[df['Stock']==s]['PCR'].values[0]})")
                else: st.write("None")
                
            st.markdown("---")
            st.info(f"🚀 **TOTAL STRONG BUY:** {', '.join(s_buy_list) if s_buy_list else 'None'}")
            st.warning(f"💀 **TOTAL STRONG SELL:** {', '.join(s_sell_list) if s_sell_list else 'None'}")

        else:
            st.error("Data Fetch Failed. Please try again.")
