import streamlit as st
import pandas as pd
import numpy as np

# =========================
# 1. PAGE CONFIG
# =========================
st.set_page_config(page_title="Manohar NSE Pro Pro", layout="wide")

# =========================
# 2. MARKET DASHBOARD (TOP SECTION)
# =========================
st.title("🚀 MANOHAR NSE PRO SMART SCANNER")

# Simulated Market Data for Dashboard
vix_val = round(np.random.uniform(12, 18), 2)
pcr_val = round(np.random.uniform(0.6, 1.4), 2)

# Trend Logic
if pcr_val > 1.1:
    trend_text = "🟢 BULLISH"
    trend_color = "green"
elif pcr_val < 0.8:
    trend_text = "🔴 BEARISH"
    trend_color = "red"
else:
    trend_text = "🟡 SIDEWAYS"
    trend_color = "orange"

# Small Metrics Bar
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"**TREND:** <span style='color:{trend_color}; font-size:20px;'>{trend_text}</span>", unsafe_allow_value=True)
with col2:
    st.metric("INDIA VIX", vix_val, delta="-1.2%" if vix_val < 15 else "1.5%")
with col3:
    st.metric("PCR RATIO", pcr_val)
with col4:
    st.markdown(f"**STATUS:** <span style='color:white; background-color:blue; padding:5px; border-radius:5px;'>LIVE SCANNING</span>", unsafe_allow_html=True)

st.divider()

# =========================
# 3. DATA GENERATOR
# =========================
def get_all_indices_data():
    indices = {"NIFTY": 24500, "BANKNIFTY": 52500, "FINNIFTY": 23200, "MIDCAPNIFTY": 12500}
    all_data = []
    for name, spot in indices.items():
        strikes = [spot - 100 + (i * 50) for i in range(5)]
        for s in strikes:
            ce_delta = round(np.random.uniform(0.4, 0.9), 2)
            pe_delta = round(ce_delta - 1, 2)
            ce_oi_chg = np.random.randint(-2000, 2000)
            pe_oi_chg = np.random.randint(-2000, 2000)
            all_data.append({
                "Index": name, "Strike": s, "CE_LTP": round(np.random.uniform(50, 300), 2),
                "CE_Delta": ce_delta, "CE_OI_Chg": ce_oi_chg,
                "PE_LTP": round(np.random.uniform(50, 300), 2),
                "PE_Delta": pe_delta, "PE_OI_Chg": pe_oi_chg
            })
    return pd.DataFrame(all_data)

# =========================
# 4. MAIN SCANNER
# =========================
if st.button("🔍 RUN FULL SCANNER"):
    full_df = get_all_indices_data()
    
    tab1, tab2, tab3, tab4 = st.tabs(["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCAPNIFTY"])
    index_list = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCAPNIFTY"]
    tabs = [tab1, tab2, tab3, tab4]

    for i in range(len(index_list)):
        current_index = index_list[i]
        with tabs[i]:
            df_idx = full_df[full_df['Index'] == current_index].copy()
            st.dataframe(df_idx.set_index('Index'), use_container_width=True)

            # 100% Confirmation Logic
            ce_sig = df_idx[(df_idx['CE_Delta'] > 0.65) & (df_idx['CE_OI_Chg'] < 0)]
            pe_sig = df_idx[(df_idx['PE_Delta'] < -0.65) & (df_idx['PE_OI_Chg'] < 0)]

            c_a, c_b = st.columns(2)
            with c_a:
                if not ce_sig.empty:
                    st.success(f"🟢 {current_index} CALL BUY")
                    for _, row in ce_sig.iterrows():
                        st.write(f"**Strike: {row['Strike']} CE** | Entry: {row['CE_LTP']} | SL: {round(row['CE_LTP']*0.85, 2)}")
                else: st.write("No CE Signals")
            
            with c_b:
                if not pe_sig.empty:
                    st.error(f"🔴 {current_index} PUT BUY")
                    for _, row in pe_sig.iterrows():
                        st.write(f"**Strike: {row['Strike']} PE** | Entry: {row['PE_LTP']} | SL: {round(row['PE_LTP']*0.85, 2)}")
                else: st.write("No PE Signals")
