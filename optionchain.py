# =========================================================
# 🚀 NSE OPTION CHAIN AI ANALYZER
# =========================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="NSE OPTION CHAIN AI ANALYZER",
    page_icon="🚀",
    layout="wide"
)

# =========================================================
# DARK UI
# =========================================================

st.markdown("""
<style>

.main {
    background-color: #0E1117;
    color: white;
}

[data-testid="stSidebar"] {
    background-color: #111827;
}

.stMetric {
    background-color: #1F2937;
    padding: 15px;
    border-radius: 12px;
}

h1,h2,h3 {
    color: white !important;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# TITLE
# =========================================================

st.title("🚀 NSE OPTION CHAIN AI ANALYZER")
st.caption("Institutional Smart Money Analysis Engine")

# =========================================================
# FILE UPLOAD
# =========================================================

uploaded_file = st.file_uploader(
    "📂 UPLOAD OPTION CHAIN FILE",
    type=["csv", "xlsx"]
)

# =========================================================
# MAIN LOGIC
# =========================================================

if uploaded_file:

    try:

        # =================================================
        # LOAD FILE
        # =================================================

        if uploaded_file.name.endswith(".csv"):

            df = pd.read_csv(uploaded_file)

        else:

            df = pd.read_excel(uploaded_file)

        st.success("✅ FILE LOADED SUCCESSFULLY")

        # =================================================
        # COLUMN CLEAN
        # =================================================

        df.columns = [
            str(col).strip().upper()
            for col in df.columns
        ]

        st.subheader("📂 RAW OPTION CHAIN DATA")

        st.dataframe(
            df,
            use_container_width=True
        )

        # =================================================
        # REQUIRED COLUMNS
        # =================================================

        required = [

            "STRIKE",
            "CALL_OI",
            "PUT_OI",
            "CALL_CHG_OI",
            "PUT_CHG_OI"
        ]

        missing = [
            col for col in required
            if col not in df.columns
        ]

        if missing:

            st.error(
                f"❌ MISSING COLUMNS : {missing}"
            )

            st.stop()

        # =================================================
        # PCR
        # =================================================

        total_call = df["CALL_OI"].sum()

        total_put = df["PUT_OI"].sum()

        pcr = (
            total_put / total_call
            if total_call > 0
            else 0
        )

        # =================================================
        # SUPPORT / RESISTANCE
        # =================================================

        support = df.loc[
            df["PUT_OI"].idxmax(),
            "STRIKE"
        ]

        resistance = df.loc[
            df["CALL_OI"].idxmax(),
            "STRIKE"
        ]

        # =================================================
        # MAX PAIN
        # =================================================

        df["TOTAL_OI"] = (
            df["CALL_OI"]
            +
            df["PUT_OI"]
        )

        max_pain = df.loc[
            df["TOTAL_OI"].idxmax(),
            "STRIKE"
        ]

        # =================================================
        # AI ANALYSIS
        # =================================================

        bullish_score = 0

        bearish_score = 0

        # PCR

        if pcr > 1:

            bullish_score += 30

        else:

            bearish_score += 30

        # PUT WRITING

        if (
            df["PUT_CHG_OI"].sum()
            >
            df["CALL_CHG_OI"].sum()
        ):

            bullish_score += 30

        else:

            bearish_score += 30

        # SMART MONEY

        max_put_change = df.loc[
            df["PUT_CHG_OI"].idxmax(),
            "STRIKE"
        ]

        max_call_change = df.loc[
            df["CALL_CHG_OI"].idxmax(),
            "STRIKE"
        ]

        # =================================================
        # SIGNAL
        # =================================================

        if bullish_score > bearish_score:

            signal = "🚀 BULLISH"

            movement = (
                f"TARGET MOVE TOWARDS "
                f"{resistance}"
            )

        elif bearish_score > bullish_score:

            signal = "🔻 BEARISH"

            movement = (
                f"TARGET MOVE TOWARDS "
                f"{support}"
            )

        else:

            signal = "⚠️ SIDEWAYS"

            movement = (
                f"RANGE BETWEEN "
                f"{support} - {resistance}"
            )

        # =================================================
        # METRICS
        # =================================================

        st.subheader("🤖 AI OPTION ANALYSIS")

        m1, m2, m3, m4, m5 = st.columns(5)

        m1.metric(
            "PCR",
            round(pcr,2)
        )

        m2.metric(
            "SUPPORT",
            int(support)
        )

        m3.metric(
            "RESISTANCE",
            int(resistance)
        )

        m4.metric(
            "MAX PAIN",
            int(max_pain)
        )

        m5.metric(
            "AI SIGNAL",
            signal
        )

        # =================================================
        # MOVEMENT
        # =================================================

        st.success(
            f"🎯 {movement}"
        )

        # =================================================
        # SMART MONEY
        # =================================================

        st.subheader("🏦 SMART MONEY FLOW")

        st.info(
            f"""
            🔥 MAX PUT WRITING : {max_put_change}

            🔥 MAX CALL WRITING : {max_call_change}
            """
        )

        # =================================================
        # BUILDUP ANALYSIS
        # =================================================

        st.subheader("📈 BUILDUP ANALYSIS")

        buildup = []

        for _, row in df.iterrows():

            strike = row["STRIKE"]

            call_oi = row["CALL_OI"]

            put_oi = row["PUT_OI"]

            call_change = row["CALL_CHG_OI"]

            put_change = row["PUT_CHG_OI"]

            # LONG BUILDUP

            if (
                put_change > 0
                and
                put_oi > call_oi
            ):

                buildup.append({

                    "STRIKE": strike,

                    "TYPE":
                    "🚀 LONG BUILDUP"
                })

            # SHORT BUILDUP

            elif (
                call_change > 0
                and
                call_oi > put_oi
            ):

                buildup.append({

                    "STRIKE": strike,

                    "TYPE":
                    "🔻 SHORT BUILDUP"
                })

        buildup_df = pd.DataFrame(buildup)

        if not buildup_df.empty:

            st.dataframe(
                buildup_df,
                use_container_width=True
            )

        # =================================================
        # OI CHART
        # =================================================

        st.subheader("📊 OI ANALYSIS")

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=df["STRIKE"],
            y=df["CALL_OI"],
            name="CALL OI"
        ))

        fig.add_trace(go.Bar(
            x=df["STRIKE"],
            y=df["PUT_OI"],
            name="PUT OI"
        ))

        fig.update_layout(
            template="plotly_dark",
            barmode="group",
            height=700
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # =================================================
        # AI STRIKE PREDICTION
        # =================================================

        st.subheader("🎯 AI STRIKE MOVEMENT")

        top_put = df.nlargest(
            3,
            "PUT_CHG_OI"
        )[
            ["STRIKE", "PUT_CHG_OI"]
        ]

        top_call = df.nlargest(
            3,
            "CALL_CHG_OI"
        )[
            ["STRIKE", "CALL_CHG_OI"]
        ]

        c1, c2 = st.columns(2)

        with c1:

            st.success(
                "🚀 STRONG PUT SIDE"
            )

            st.dataframe(
                top_put,
                use_container_width=True
            )

        with c2:

            st.error(
                "🔻 STRONG CALL SIDE"
            )

            st.dataframe(
                top_call,
                use_container_width=True
            )

    except Exception as e:

        st.error(f"❌ ERROR : {e}")

else:

    st.info(
        "📂 PLEASE UPLOAD OPTION CHAIN FILE"
    )
