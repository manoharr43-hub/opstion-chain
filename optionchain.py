import streamlit as st
import pandas as pd
import numpy as np

# =========================
# 1. PAGE CONFIG
# =========================
st.set_page_config(page_title="Manohar NSE Pro Dashboard", layout="wide")

# =========================
# 2. LIVE INDEX PRICES (TOP SECTION)
# =========================
st.title("🚀 MANOHAR NSE PRO SMART SCANNER")

# Simulated Live Prices (రియల్ టైమ్ లో ఇవి మారుతూ ఉంటాయి)
nifty_spot = 24510.50
bnk_nifty_spot = 52480.20
fin_nifty_spot = 23150.75
mid_nifty_spot = 12420.30

# పైన ఇండెక్స్ ధరలను చూపించే కాలమ్స్
cp1, cp2, cp3, cp4 = st.columns(4)
cp1.metric("NIFTY 50", f"{nifty_spot}", "12.50")
cp2.metric("BANK NIFTY", f"{bnk_nifty_spot}", "-45.30")
cp3.metric("FIN NIFTY", f"{fin_nifty_spot}", "5.10")
cp4.metric("MIDCAP NIFTY", f"{mid_nifty_spot}", "22.40")

st.divider()

# =========================
# 3. MARKET INDICATORS (TREND, VIX, PCR)
# =========================
vix_val = round(np.random.uniform(12, 18), 2)
pcr_val = round(np.random.uniform(0.6, 1.4), 2)

if pcr_val > 1.1:
    trend_status = "BULLISH 🟢"
elif pcr_val < 0.8:
    trend_status = "BEARISH 🔴"
else:
    trend_status = "SIDEWAYS 🟡"

m1, m2, m3 = st.columns(3)
m1.metric("MARKET TREND", trend_status)
m2.metric("INDIA VIX", f"{vix_val}")
m3.metric("PCR RATIO", f"{pcr_val}")

st.divider()

# =========================
# 4. DATA GENERATOR
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
# 5. MAIN SCANNER
# =========================
if st.button("🔍 RUN FULL SCANNER"):
    full_df = get_all_indices_data()
    
    tabs = st.tabs(["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCAPNIFTY"])
    index_list = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCAPNIFTY"]

    for i in range(len(index_list)):
        current_index = index_list[i]
        with tabs[i]:
            df_idx = full_df[full_df['Index'] == current_index].copy()
            st.dataframe(df_idx.set_index('Index'), use_container_width=True)

            # 100% Confirmation Logic
            ce_sig = df_idx[(df_idx['CE_Delta'] > 0.65) & (df_idx['CE_OI_Chg'] < 0)]
            pe_sig = df_idx[(df_idx['PE_Delta'] < -0.65) & (df_idx['PE_OI_Chg'] < 0)]

            col_a, col_b = st.columns(2)
            with col_a:
                if not ce_sig.empty:
                    st.success(f"🟢 {current_index} CALL BUY")
                    for _, row in ce_sig.iterrows():
                        st.write(f"**Strike: {row['Strike']} CE** | Entry: {row['CE_LTP']} | SL: {round(row['CE_LTP']*0.85, 2)}")
                else: st.write("No CE Signals")
            
            with col_b:
                if not pe_sig.empty:
                    st.error(f"🔴 {current_index} PUT BUY")
                    for _, row in pe_sig.iterrows():
                        st.write(f"**Strike: {row['Strike']} PE** | Entry: {row['PE_LTP']} | SL: {round(row['PE_LTP']*0.85, 2)}")
                else: st.write("No PE Signals")
