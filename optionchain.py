import streamlit as st
import pandas as pd
import plotly.express as px
from nsepython import option_chain

st.set_page_config(page_title="Nifty Option Chain", layout="wide")
st.title("📊 NSE Nifty Option Chain Analysis")

# =============================
# FUNCTION
# =============================
@st.cache_data(ttl=60)
def get_data():
    try:
        data = option_chain("NIFTY")

        rows = []

        for item in data["records"]["data"]:

            strike = item.get("strikePrice", 0)

            call_oi = item.get("CE", {}).get("openInterest", 0)
            put_oi = item.get("PE", {}).get("openInterest", 0)

            rows.append({
                "Strike": strike,
                "Call_OI": call_oi,
                "Put_OI": put_oi
            })

        df = pd.DataFrame(rows)
        return df

    except Exception as e:
        st.error(f"Error: {e}")
        return None


# =============================
# UI
# =============================
if st.sidebar.button("Fetch Data"):

    df = get_data()

    if df is not None and not df.empty:

        max_call = df.loc[df["Call_OI"].idxmax()]
        max_put = df.loc[df["Put_OI"].idxmax()]

        c1, c2 = st.columns(2)
        c1.metric("🔴 Resistance", int(max_call["Strike"]))
        c2.metric("🟢 Support", int(max_put["Strike"]))

        st.subheader("Call vs Put OI")

        df_chart = df.sort_values("Strike").tail(30)

        fig = px.bar(df_chart, x="Strike", y=["Call_OI", "Put_OI"], barmode="group")
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(df)

    else:
        st.error("Data load avvaledu")

else:
    st.info("Click Fetch Data")
