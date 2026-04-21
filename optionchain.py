import streamlit as st
import pandas as pd
import io

# --- UI సెటప్ ---
st.set_page_config(page_title="NSE Option Chain Analyzer", layout="wide")
st.title("📊 NSE Option Chain File Analyzer")

st.markdown("""
### 📥 NSE నుండి డౌన్లోడ్ చేసిన CSV ఫైల్‌ను ఇక్కడ అప్‌లోడ్ చేయండి
మీరు NSE వెబ్‌సైట్‌లో 'Download CSV' నొక్కిన ఫైల్‌ను ఇక్కడ వాడవచ్చు.
""")

# --- ఫైల్ అప్‌లోడర్ ---
uploaded_file = st.file_uploader("Choose NSE Option Chain CSV", type="csv")

if uploaded_file is not None:
    try:
        # NSE CSV ఫైల్స్ సాధారణంగా మొదటి కొన్ని లైన్లు హెడర్స్ ఉంటాయి, వాటిని స్కిప్ చేయాలి
        df = pd.read_csv(uploaded_file, skiprows=1)
        
        # అవసరమైన కాలమ్స్ మాత్రమే ఫిల్టర్ చేయడం
        # NSE ఫైల్‌లో కాలమ్ పేర్లు కొంచెం భిన్నంగా ఉండవచ్చు
        cols_to_keep = ['STRIKE PRICE', 'CHNG IN OI', 'OI', 'LTP', 'IV', 'VOLUME', 
                        'CHNG IN OI.1', 'OI.1', 'LTP.1', 'IV.1', 'VOLUME.1']
        
        # కాలమ్ పేర్లను మనకు అర్థమయ్యేలా మార్చడం
        df_clean = df[cols_to_keep].copy()
        df_clean.columns = [
            'Strike', 'CE_Chng_OI', 'CE_OI', 'CE_LTP', 'CE_IV', 'CE_Vol',
            'PE_Chng_OI', 'PE_OI', 'PE_LTP', 'PE_IV', 'PE_Vol'
        ]

        # 1. Active Strike Price ని కనుక్కోవడం (ఎక్కడైతే OI మార్పు ఎక్కువగా ఉందో)
        max_ce_oi = df_clean.loc[df_clean['CE_Chng_OI'].idxmax()]
        max_pe_oi = df_clean.loc[df_clean['PE_Chng_OI'].idxmax()]

        # --- అనలిటిక్స్ డిస్ప్లే ---
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Resistance (Max CE OI Chng)", f"{max_ce_oi['Strike']}")
            st.caption("Call Writers ఇక్కడ ఎక్కువగా యాక్టివ్ గా ఉన్నారు.")

        with col2:
            st.metric("Support (Max PE OI Chng)", f"{max_pe_oi['Strike']}")
            st.caption("Put Writers ఇక్కడ సపోర్ట్ ఇస్తున్నారు.")

        with col3:
            total_ce_oi = df_clean['CE_OI'].sum()
            total_pe_oi = df_clean['PE_OI'].sum()
            pcr = round(total_pe_oi / total_ce_oi, 2)
            st.metric("Overall PCR", pcr)
            st.caption(">1 అంటే Bullish, <1 అంటే Bearish")

        # --- టేబుల్ డిస్ప్లే ---
        st.subheader("📋 Option Chain Data")
        
        # Strike Price ఆధారంగా చార్ట్ మూమెంట్ ఏ వైపు ఉందో కలర్స్ తో చూపడం
        def highlight_movement(row):
            if row['CE_Chng_OI'] > row['PE_Chng_OI']:
                return ['background-color: #ffcccc'] * len(row) # Red for resistance
            else:
                return ['background-color: #ccffcc'] * len(row) # Green for support

        st.dataframe(df_clean.style.apply(highlight_movement, axis=1), use_container_width=True)

    except Exception as e:
        st.error(f"ఫైల్ ప్రాసెస్ చేయడంలో ఇబ్బంది ఉంది: {e}")
        st.info("గమనిక: NSE నుండి డౌన్లోడ్ చేసిన ఒరిజినల్ CSV ఫైల్‌ను మాత్రమే అప్‌లోడ్ చేయండి.")

else:
    st.info("ముందుగా NSE వెబ్‌సైట్ నుండి ఆప్షన్ చైన్ CSV ఫైల్‌ను డౌన్లోడ్ చేసి ఇక్కడ అప్‌లోడ్ చేయండి.")
    
