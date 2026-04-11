import streamlit as st
import pandas as pd
import numpy as np

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Manohar NSE Pro 100%", layout="wide")
st.title("🎯 MANOHAR NSE PRO - 100% CONFIRMATION SCANNER")

# =========================
# DATA GENERATOR
# =========================
def generate_market_data():
    spot = 24500
    strikes = [spot - 200 + (i * 50) for i in range(10)]
    
    data = []
    for s in strikes:
        # సిమ్యులేటెడ్ లాజిక్
        ce_delta = round(np.random.uniform(0.1, 0.9), 2)
        pe_delta = round(ce_delta - 1, 2)
        ce_oi_chg = np.random.randint(-1000, 2000)
        pe_oi_chg = np.random.randint(-1000, 2000)
        
        data.append({
            "Strike Price": s,
            "CE LTP": round(np.random.uniform(50, 250), 2),
            "CE Delta": ce_delta,
            "CE OI Chg": ce_oi_chg,
            "PE LTP": round(np.random.uniform(50, 250), 2),
            "PE Delta": pe_delta,
            "PE OI Chg": pe_oi_chg
        })
    return pd.DataFrame(data), spot

# =========================
# RUN SCANNER
# =========================
if st.button("RUN 100% CONFIRMATION SCAN"):
    df, spot = generate_market_data()
    
    st.subheader(f"📊 Market Spot: {spot}")
    st.dataframe(df, use_container_width=True)

    st.divider()
    
    # --- 100% CONFIRMATION LOGIC ---
    # Call Side: Delta > 0.65 AND OI Change is Negative (Short Covering)
    ce_signals = df[(df['CE Delta'] > 0.65) & (df['CE OI Chg'] < 0)]
    
    # Put Side: Delta < -0.65 AND OI Change is Negative (Long Unwinding)
    pe_signals = df[(df['PE Delta'] < -0.65) & (df['PE OI Chg'] < 0)]

    col1, col2 = st.columns(2)

    with col1:
        st.success("🟢 100% CE (CALL) CONFIRMATION")
        if not ce_signals.empty:
            for _, row in ce_signals.iterrows():
                st.markdown(f"### Buy Call: **{row['Strike Price']} CE**")
                st.write(f"Entry: ₹{row['CE LTP']} | SL: ₹{round(row['CE LTP']*0.85, 2)} | Tgt: ₹{round(row['CE LTP']*1.3, 2)}")
        else:
            st.info("No Strong Call Signals")

    with col2:
        st.error("🔴 100% PE (PUT) CONFIRMATION")
        if not pe_signals.empty:
            for _, row in pe_signals.iterrows():
                st.markdown(f"### Buy Put: **{row['Strike Price']} PE**")
                st.write(f"Entry: ₹{row['PE LTP']} | SL: ₹{round(row['PE LTP']*0.85, 2)} | Tgt: ₹{round(row['PE LTP']*1.3, 2)}")
        else:
            st.info("No Strong Put Signals")

st.info("Note: Delta > 0.65 మరియు OI తగ్గుతున్న స్ట్రైక్ ప్రైస్ లు ఇక్కడ కనిపిస్తాయి.")
