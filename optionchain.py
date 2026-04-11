import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# ==========================================
# 1. AUTO REFRESH (5 MINUTES)
# ==========================================
st_autorefresh(interval=5 * 60 * 1000, key="manohar_pro_refresh")

# ==========================================
# 2. PAGE CONFIG
# ==========================================
st.set_page_config(page_title="Manohar AI Market Scanner", layout="wide")

# ==========================================
# 3. REAL INDEX DATA (YFINANCE)
# ==========================================
def get_live_index():
    symbols = {
        "NIFTY": "^NSEI",
        "BANKNIFTY": "^NSEBANK",
        "FINNIFTY": "^CNXFINANCE",
        "MIDCAPNIFTY": "^NSEMDCP50"
    }
    
    result = {}
    
    for name, symbol in symbols.items():
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d", interval="5m")
            
            if not data.empty:
                last = data.iloc[-1]
                prev = data.iloc[-2]
                
                price = round(last["Close"], 2)
                change = round(price - prev["Close"], 2)
                
                result[name] = {
                    "price": price,
                    "chg": change
                }
            else:
                result[name] = {"price": "N/A", "chg": "0"}
                
        except:
            result[name] = {"price": "Error", "chg": "0"}
    
    return result

idx_prices = get_live_index()

# ==========================================
# 4. UI HEADER
# ==========================================
st.title("🚀 MANOHAR NSE PRO - SMART SCANNER")

c1, c2, c3, c4 = st.columns(4)
c1.metric("NIFTY 50", idx_prices["NIFTY"]["price"], idx_prices["NIFTY"]["chg"])
c2.metric("BANK NIFTY", idx_prices["BANKNIFTY"]["price"], idx_prices["BANKNIFTY"]["chg"])
c3.metric("FIN NIFTY", idx_prices["FINNIFTY"]["price"], idx_prices["FINNIFTY"]["chg"])
c4.metric("MIDCAP NIFTY", idx_prices["MIDCAPNIFTY"]["price"], idx_prices["MIDCAPNIFTY"]["chg"])

st.divider()

# ==========================================
# 5. SIDEBAR INDEX SELECT
# ==========================================
selected_idx = st.sidebar.selectbox(
    "🎯 SELECT INDEX TO SCAN",
    ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCAPNIFTY"]
)

# PCR (still simulated)
pcr_values = {
    "NIFTY": 1.15,
    "BANKNIFTY": 0.75,
    "FINNIFTY": 0.95,
    "MIDCAPNIFTY": 1.30
}

current_pcr = pcr_values[selected_idx]
vix_val = 14.20

# Trend logic
if current_pcr > 1.1:
    trend_text, t_color = "BULLISH 🟢", "success"
elif current_pcr < 0.8:
    trend_text, t_color = "BEARISH 🔴", "error"
else:
    trend_text, t_color = "SIDEWAYS 🟡", "warning"

m1, m2, m3 = st.columns(3)

with m1:
    st.write(f"**{selected_idx} TREND:**")
    if t_color == "success":
        st.success(trend_text)
    elif t_color == "error":
        st.error(trend_text)
    else:
        st.warning(trend_text)

m2.metric("INDIA VIX", vix_val)
m3.metric(f"{selected_idx} PCR", current_pcr)

st.divider()

# ==========================================
# 6. AI SIGNAL GENERATOR (OLD LOGIC SAFE)
# ==========================================
def get_signals(index_name):
    base = {
        "NIFTY": 24500,
        "BANKNIFTY": 52500,
        "FINNIFTY": 23100,
        "MIDCAPNIFTY": 12400
    }
    
    spot = base[index_name]
    gap = 100 if "BANK" in index_name else 50
    
    strikes = [spot - (gap*2) + (i*gap) for i in range(5)]
    
    data = []
    
    for s in strikes:
        ce_oi_chg = np.random.randint(-5000, 5000)
        pe_oi_chg = np.random.randint(-5000, 5000)
        
        ce_ltp = round(np.random.uniform(100, 300), 2)
        pe_ltp = round(np.random.uniform(100, 300), 2)
        
        signal = "Neutral"
        
        if ce_oi_chg < -3500:
            signal = "STRONG BUY CE"
        elif pe_oi_chg < -3500:
            signal = "STRONG BUY PE"
        
        data.append({
            "Strike": s,
            "CE_LTP": ce_ltp,
            "CE_OI_Chg": ce_oi_chg,
            "PE_LTP": pe_ltp,
            "PE_OI_Chg": pe_oi_chg,
            "AI_Signal": signal
        })
    
    return pd.DataFrame(data)

# ==========================================
# 7. SIGNAL DISPLAY
# ==========================================
df = get_signals(selected_idx)

st.subheader(f"📊 AI ANALYSIS & TRADE SIGNALS: {selected_idx}")

signals = df[df['AI_Signal'] != "Neutral"]

if not signals.empty:
    for _, row in signals.iterrows():
        
        if "CE" in row['AI_Signal']:
            entry = row['CE_LTP']
            
            st.success(f"🔥 {selected_idx} {row['Strike']} CE SIGNAL")
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("ENTRY", entry)
            c2.metric("SL", round(entry*0.8, 2))
            c3.metric("TG1", round(entry*1.2, 2))
            c4.metric("TG2", round(entry*1.5, 2))
        
        else:
            entry = row['PE_LTP']
            
            st.error(f"📉 {selected_idx} {row['Strike']} PE SIGNAL")
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("ENTRY", entry)
            c2.metric("SL", round(entry*0.8, 2))
            c3.metric("TG1", round(entry*1.2, 2))
            c4.metric("TG2", round(entry*1.5, 2))

st.divider()

# ==========================================
# 8. FULL TABLE
# ==========================================
st.write("FULL DATA TABLE")
st.dataframe(df.set_index("Strike"), use_container_width=True)

# ==========================================
# 9. FOOTER
# ==========================================
st.sidebar.markdown(
    f"⏰ Last Refresh: {pd.Timestamp.now().strftime('%H:%M:%S')}"
)
# ===============================
# ADD THIS BELOW YOUR EXISTING CODE
# ===============================

st.divider()
st.subheader("📈 LIVE MARKET TREND")

# ==========================================
# LIVE CHART
# ==========================================
def get_chart(symbol):
    data = yf.Ticker(symbol).history(period="1d", interval="5m")
    return data

symbol_map = {
    "NIFTY": "^NSEI",
    "BANKNIFTY": "^NSEBANK",
    "FINNIFTY": "^CNXFINANCE",
    "MIDCAPNIFTY": "^NSEMDCP50"
}

chart_data = get_chart(symbol_map[selected_idx])

if not chart_data.empty:
    st.line_chart(chart_data["Close"])

# ==========================================
# SUPPORT & RESISTANCE
# ==========================================
st.subheader("🎯 SUPPORT & RESISTANCE")

if not chart_data.empty:
    support = round(chart_data["Low"].min(), 2)
    resistance = round(chart_data["High"].max(), 2)
    
    c1, c2 = st.columns(2)
    c1.metric("SUPPORT", support)
    c2.metric("RESISTANCE", resistance)

# ==========================================
# STRONG SIGNAL FILTER
# ==========================================
st.subheader("🔥 STRONG AI SIGNALS ONLY")

strong_signals = []

for _, row in df.iterrows():
    
    if row["CE_OI"] > row["PE_OI"] * 2:
        strong_signals.append(("PE", row))
    elif row["PE_OI"] > row["CE_OI"] * 2:
        strong_signals.append(("CE", row))

if strong_signals:
    for sig_type, row in strong_signals:
        
        if sig_type == "CE":
            entry = row["CE_LTP"]
            st.success(f"🚀 STRONG BUY CE - {selected_idx} {row['Strike']}")
        else:
            entry = row["PE_LTP"]
            st.error(f"📉 STRONG BUY PE - {selected_idx} {row['Strike']}")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("ENTRY", entry)
        c2.metric("SL", round(entry*0.8, 2))
        c3.metric("TG1", round(entry*1.3, 2))
        c4.metric("TG2", round(entry*1.6, 2))

else:
    st.info("No strong signals right now")

# ==========================================
# ALERT SYSTEM
# ==========================================
st.subheader("🚨 MARKET ALERT")

price = idx_data[selected_idx]["price"]

if price > resistance:
    st.success("🔥 BREAKOUT DETECTED (BUY)")
elif price < support:
    st.error("💥 BREAKDOWN DETECTED (SELL)")
else:
    st.warning("Market inside range")
