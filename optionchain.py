import streamlit as st
import pandas as pd

# --- UI Layout ---
st.set_page_config(page_title="NSE AI PRO Terminal", layout="wide")
st.title("🚀 NSE AI PRO - Individual Index Analyzer")

uploaded_file = st.file_uploader("NSE CSV ఫైల్‌ను ఇక్కడ అప్‌లోడ్ చేయండి", type="csv")

if uploaded_file is not None:
    try:
        # NSE CSV రీడింగ్
        df = pd.read_csv(uploaded_file, skiprows=1)
        df.columns = df.columns.str.strip()

        # Strike Price కాలమ్ ని గుర్తించడం
        strike_col = [col for col in df.columns if 'STRIKE' in col.upper()][0]
        
        # డేటా లోడింగ్ (మధ్యలో ఉండే Strike Price కి ఇటు అటు డేటాను విడదీయడం)
        # సాధారణంగా NSE ఫైల్ లో Strike Price కి ఎడమ వైపు CE, కుడి వైపు PE ఉంటాయి.
        
        # 1. కాల్ సైడ్ డేటా (Call Side)
        ce_data = df.iloc[:, :df.columns.get_loc(strike_col)].copy()
        
        # 2. పుట్ సైడ్ డేటా (Put Side)
        pe_data = df.iloc[:, df.columns.get_loc(strike_col)+1:].copy()
        
        # --- మార్కెట్ అనాలిసిస్ బానర్ ---
        total_ce_oi = ce_data.iloc[:, 1].sum() # 2nd column as OI
        total_pe_oi = pe_data.iloc[:, 1].sum() # 2nd column as OI
        pcr = round(total_pe_oi / total_ce_oi, 2) if total_ce_oi > 0 else 0
        
        direction = "SIDEWAYS"
        color = "gray"
        if pcr > 1.2:
            direction = "BULLISH (పైకి)"
            color = "green"
        elif pcr < 0.8:
            direction = "BEARISH (కిందకి)"
            color = "red"

        st.subheader(f"📈 మార్కెట్ ట్రెండ్: :{color}[{direction}] | PCR: {pcr}")
        st.divider()

        # --- ఇండివిడ్యువల్ షో (CE | STRIKE | PE) ---
        st.subheader("📋 Option Chain (Individual View)")
        
        # మనం స్ట్రైక్ ప్రైస్ ని సెంటర్ లో పెట్టి ఒక కొత్త టేబుల్ లాగా చూపిద్దాం
        final_view = pd.DataFrame({
            "CALLS_OI": ce_data.iloc[:, 1],
            "CALLS_CHNG_OI": ce_data.iloc[:, 2],
            "CALLS_LTP": ce_data.iloc[:, 5], # LTP position usually 5 or 6
            "STRIKE": df[strike_col],
            "PUTS_LTP": pe_data.iloc[:, 5],
            "PUTS_CHNG_OI": pe_data.iloc[:, 2],
            "PUTS_OI": pe_data.iloc[:, 1]
        })

        # టేబుల్ ని అందంగా చూపడం
        def color_map(val):
            if isinstance(val, str): return ''
            return 'color: green' if val > 0 else 'color: red'

        st.dataframe(final_view.style.applymap(color_map, subset=['CALLS_CHNG_OI', 'PUTS_CHNG_OI']), use_container_width=True)

        # --- Buy/Sell సిగ్నల్స్ ---
        st.divider()
        st.subheader("🎯 Active Strike Signals")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("🟢 **Buy Zone (Strong Support)**")
            buy_strikes = final_view[final_view['PUTS_CHNG_OI'] > final_view['CALLS_CHNG_OI']].head(5)
            st.table(buy_strikes[['STRIKE', 'PUTS_CHNG_OI', 'PUTS_LTP']])
            
        with col2:
            st.write("🔴 **Sell Zone (Strong Resistance)**")
            sell_strikes = final_view[final_view['CALLS_CHNG_OI'] > final_view['PUTS_CHNG_OI']].head(5)
            st.table(sell_strikes[['STRIKE', 'CALLS_CHNG_OI', 'CALLS_LTP']])

    except Exception as e:
        st.error(f"Analysis Error: {e}")
else:
    st.info("NSE CSV ఫైల్‌ను అప్‌లోడ్ చేయండి. అప్పుడు మీకు Calls మరియు Puts డేటా విడివిడిగా కనిపిస్తుంది.")
