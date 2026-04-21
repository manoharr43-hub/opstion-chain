import streamlit as st
import pandas as pd

# --- UI Layout ---
st.set_page_config(page_title="NSE AI PRO - High Movement Tracker", layout="wide")
st.title("🚀 NSE AI PRO - High Movement Analysis")

# --- Cleaning Function ---
def clean_numeric(val):
    if isinstance(val, str):
        val = val.replace(',', '').replace('-', '0')
    try:
        return pd.to_numeric(val)
    except:
        return 0

# Side bar for file uploads
st.sidebar.header("📁 Data Upload")
file1 = st.sidebar.file_uploader("NSE Option Chain CSV", type="csv")

if file1 is not None:
    try:
        df = pd.read_csv(file1, skiprows=1)
        df.columns = df.columns.str.strip()
        df = df.map(clean_numeric)

        # Strike Price identification
        strike_col = [col for col in df.columns if 'STRIKE' in col.upper()][0]
        strike_idx = df.columns.get_loc(strike_col)
        
        ce_df = df.iloc[:, :strike_idx]
        pe_df = df.iloc[:, strike_idx+1:]

        # మెయిన్ అనాలిసిస్ డేటాఫ్రేమ్
        analysis_df = pd.DataFrame({
            "CE_OI_CHNG": ce_df.iloc[:, 2],
            "CE_LTP": ce_df.iloc[:, 5],
            "STRIKE": df[strike_col],
            "PE_LTP": pe_df.iloc[:, 5],
            "PE_OI_CHNG": pe_df.iloc[:, 2]
        })

        # --- 🟢 HIGH MOVEMENT BOXES (NEW ADDITION) ---
        st.subheader("🔥 High Movement Strike List")
        col_ce, col_pe = st.columns(2)

        with col_ce:
            st.markdown("""
                <div style="background-color:#1e4620; padding:10px; border-radius:10px; border: 2px solid #00ff00;">
                    <h3 style="color:#00ff00; text-align:center; margin:0;">📈 Top CE Movement (Resistance)</h3>
                </div>
            """, unsafe_allow_html=True)
            # CE OI Change ఎక్కువగా ఉన్న టాప్ 3 స్ట్రైక్స్
            top_ce = analysis_df.nlargest(3, 'CE_OI_CHNG')[['STRIKE', 'CE_OI_CHNG', 'CE_LTP']]
            st.table(top_ce)

        with col_pe:
            st.markdown("""
                <div style="background-color:#4a1c1c; padding:10px; border-radius:10px; border: 2px solid #ff4b4b;">
                    <h3 style="color:#ff4b4b; text-align:center; margin:0;">📉 Top PE Movement (Support)</h3>
                </div>
            """, unsafe_allow_html=True)
            # PE OI Change ఎక్కువగా ఉన్న టాప్ 3 స్ట్రైక్స్
            top_pe = analysis_df.nlargest(3, 'PE_OI_CHNG')[['STRIKE', 'PE_OI_CHNG', 'PE_LTP']]
            st.table(top_pe)

        st.divider()

        # --- మెయిన్ టేబుల్ విత్ Buy/Sell సిగ్నల్స్ ---
        st.subheader("📋 Detailed Option Chain Analyzer")
        
        def get_signal(row):
            if row['PE_OI_CHNG'] > row['CE_OI_CHNG'] * 1.5: return "🟢 BUY"
            if row['CE_OI_CHNG'] > row['PE_OI_CHNG'] * 1.5: return "🔴 SELL"
            return "⚪ WAIT"

        analysis_df['SIGNAL'] = analysis_df.apply(get_signal, axis=1)
        
        # టేబుల్ ప్రదర్శన
        st.dataframe(analysis_df.style.map(
            lambda x: 'background-color: #006400; color: white' if x == '🟢 BUY' else 
            ('background-color: #8b0000; color: white' if x == '🔴 SELL' else ''), 
            subset=['SIGNAL']), use_container_width=True)

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("మనోహర్ గారు, హై మూమెంట్ స్ట్రైక్స్ చూడటానికి NSE ఫైల్ అప్‌లోడ్ చేయండి.")
    
