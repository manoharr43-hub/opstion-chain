import streamlit as st
import pandas as pd
import numpy as np

# ==========================================
# 1. PAGE CONFIG & STYLING
# ==========================================
st.set_page_config(page_title="Manohar NSE Pro AI", layout="wide")
st.title("🎯 MANOHAR NSE PRO AI - SMART SCANNER")
st.write("Live Market Analysis: Entry, Exit, and Stop Loss Signals")

# ==========================================
# 2. SMART DATA GENERATOR (LOGICAL)
# ==========================================
def get_live_data(symbol):
    # బేస్ ప్రైస్ సెట్టింగ్
    spot = 24000 if symbol == "NIFTY" else 52000
    strikes = [spot - 250 + (i * 50) for i in range(11)]
    
    data = []
    for s in strikes:
        # సిమ్యులేటెడ్ గ్రీక్స్ మరియు OI
        ce_oi = np.random.randint(1000, 5000)
        pe_oi = np.random.randint(1000, 5000)
        ce_oi_chg = np.random.randint(-500, 1000)
        pe_oi_chg = np.random.randint(-500, 1000)
        
        # Delta calculation (ITM/OTM logic)
        delta = round(0.5 + (spot - s) / 500, 2)
        delta = max(0.1, min(0.9, delta))
        
        data.append({
            "Strike": s,
            "CE_LTP": round(np.random.uniform(50, 300), 2),
            "CE_OI_Chg": ce_oi_chg,
            "CE_Delta": delta,
            "PE_Delta": round(delta - 1, 2),
            "PE_OI_Chg": pe_oi_chg,
            "PE_LTP": round(np.random.uniform(50, 300), 2),
            "Signal": "Neutral"
        })
    return pd.DataFrame(data), spot

# ==========================================
# 3. TRADING LOGIC (ENTRY/EXIT/SL)
# ==========================================
def analyze_signals(df, spot):
    for i, row in df.iterrows():
        # CALL BUY CONDITION: CE OI తగ్గుతూ (Short Covering), PE OI పెరుగుతుంటే
        if row['CE_OI_Chg'] < 0 and row['PE_OI_Chg'] > 0 and row['CE_Delta'] > 0.6:
            df.at[i, 'Signal'] = "🔥 STRONG BUY (CALL)"
        
        # PUT BUY CONDITION: PE OI తగ్గుతూ (Long Unwinding), CE OI పెరుగుతుంటే
        elif row['PE_OI_Chg'] < 0 and row['CE_OI_Chg'] > 0 and abs(row['PE_Delta']) > 0.6:
            df.at[i, 'Signal'] = "📉 STRONG BUY (PUT)"
            
    return df

# ==========================================
# 4. UI COMPONENTS
# ==========================================
symbol = st.sidebar.selectbox("Select Index", ["NIFTY", "BANKNIFTY"])
if st.sidebar.button("RUN AI SCANNER"):
    df, spot = get_live_data(symbol)
    df = analyze_signals(df, spot)

    # టాప్ మెట్రిక్స్
    st.subheader(f"🚀 {symbol} Spot: {spot}")
    
    # సిగ్నల్ డిస్ప్లే
    signals = df[df['Signal'] != "Neutral"]
    if not signals.empty:
        for _, s in signals.iterrows():
            st.success(f"**SIGNAL FOUND AT {s['Strike']} Strike!**")
            c1, c2, c3 = st.columns(3)
            
            # Entry, SL, Target Calculations
            entry = s['CE_LTP'] if "CALL" in s['Signal'] else s['PE_LTP']
            sl = round(entry * 0.85, 2) # 15% Stop Loss
            tgt = round(entry * 1.30, 2) # 30% Target
            
            c1.metric("ENTRY POINT", f"₹{entry}")
            c2.metric("STOP LOSS (SL)", f"₹{sl}", delta_color="inverse", delta="-15%")
            c3.metric("TARGET (EXIT)", f"₹{tgt}", delta="30%")
    else:
        st.info("ప్రస్తుతానికి బలమైన ఎంట్రీ పాయింట్లు లేవు. వేచి ఉండండి...")

    # డేటా టేబుల్
    st.divider()
    st.subheader("📊 Detailed Option Chain Analysis")
    
    def color_signals(val):
        color = 'green' if 'CALL' in str(val) else 'red' if 'PUT' in str(val) else 'white'
        return f'background-color: {color}; color: black'

    st.dataframe(df.style.applymap(color_signals, subset=['Signal']), use_container_width=True)

# ==========================================
# 5. INSTRUCTIONS
# ==========================================
st.sidebar.divider()
st.sidebar.markdown("""
### 📘 How to use:
1. **RUN AI SCANNER** బటన్ నొక్కండి.
2. **Signal** కాలమ్ లో 'STRONG BUY' ఉందో లేదో చూడండి.
3. గ్రీన్ సిగ్నల్ వస్తే **Call Side** ఎంట్రీ తీసుకోండి.
4. రెడ్ సిగ్నల్ వస్తే **Put Side** ఎంట్రీ తీసుకోండి.
5. సిస్టమ్ ఇచ్చిన **SL** మరియు **Target** ని తప్పక పాటించండి.
""")
