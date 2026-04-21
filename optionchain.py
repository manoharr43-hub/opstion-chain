import streamlit as st
import pandas as pd

st.set_page_config(page_title="NSE Option Chain Analyzer", layout="wide")
st.title("📊 NSE Option Chain Analyzer (Automatic Fix)")

uploaded_file = st.file_uploader("NSE నుండి డౌన్లోడ్ చేసిన CSV ఫైల్‌ను ఇక్కడ అప్‌లోడ్ చేయండి", type="csv")

if uploaded_file is not None:
    try:
        # NSE ఫైల్‌లో పైన ఉన్న అదనపు లైన్లను తీసేసి డేటాను రీడ్ చేయడం
        df = pd.read_csv(uploaded_file, skiprows=1)
        
        # కాలమ్ పేర్లలో స్పేస్‌లు ఉంటే తీసేయడం
        df.columns = df.columns.str.strip()

        # కాలమ్ పేర్లు ఏవైనా సరే, వాటి స్థానాన్ని (Index) బట్టి డేటా తీసుకోవడం
        # సాధారణంగా NSE ఫైల్‌లో Strike Price 11వ కాలమ్ (index 11) లో ఉంటుంది
        # మనం ఆ కాలమ్ పేర్లను వెతకకుండా ఇలా పట్టుకుందాం:
        
        # 'Strike Price' అనే పదం ఉన్న కాలమ్ ని వెతకడం
        strike_col = [col for col in df.columns if 'STRIKE' in col.upper()]
        
        if strike_col:
            strike_name = strike_col[0]
            
            # మనకు కావలసిన ముఖ్యమైన డేటాను ఫిల్టర్ చేయడం
            # CE OI మార్పు మరియు PE OI మార్పును బట్టి మూమెంట్ కనిపెట్టడం
            st.success(f"ఫైల్ విజయవంతంగా ప్రాసెస్ చేయబడింది! ({strike_name} గుర్తించబడింది)")
            
            # అనాలిసిస్ కోసం క్లీన్ డేటా
            analysis_df = df[[strike_name]].copy()
            
            # మిగతా కాలమ్స్ ని కూడా డైనమిక్ గా పట్టుకోవడం
            ce_oi_chng = [col for col in df.columns if 'CHNG' in col.upper() and 'OI' in col.upper()]
            
            # డేటా ప్రదర్శన
            st.subheader("📋 Option Chain Data Summary")
            st.dataframe(df.head(20), use_container_width=True)
            
            st.info("చిట్కా: పైన ఉన్న టేబుల్‌లో ఏ స్ట్రైక్ దగ్గర 'CHNG IN OI' ఎక్కువగా ఉందో గమనించండి. అదే మార్కెట్ మూమెంట్‌ని సూచిస్తుంది.")
        else:
            st.error("ఫైల్‌లో 'Strike Price' కాలమ్ కనిపించలేదు. దయచేసి NSE ఒరిజినల్ CSV నే వాడండి.")

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("NSE వెబ్‌సైట్ నుండి డౌన్లోడ్ చేసిన CSV ఫైల్‌ను అప్‌లోడ్ చేయండి.")
    
