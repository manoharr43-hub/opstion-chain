# ===============================
# SIGNALS + TABLE (UPDATED)
# ===============================
st.subheader("🔥 AI SIGNALS & ANALYSIS")

try:
    if df is None or df.empty:
        st.warning("⚠️ No data available")
    else:
        # 1. PCR Calculation (Put-Call Ratio)
        total_ce_oi = df['CE_OI'].sum()
        total_pe_oi = df['PE_OI'].sum()
        pcr = round(total_pe_oi / total_ce_oi, 2) if total_ce_oi > 0 else 0

        # PCR Display with Color Logic
        if pcr > 1:
            st.markdown(f"### 📈 Index: {selected_idx} | PCR: <span style='color:green'>{pcr} (Bullish)</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"### 📉 Index: {selected_idx} | PCR: <span style='color:red'>{pcr} (Bearish)</span>", unsafe_allow_html=True)

        signals_found = False
        st.divider()

        for _, row in df.iterrows():
            ce = row.get("CE_OI", 0)
            pe = row.get("PE_OI", 0)
            strike = row.get("Strike", 0)

            if ce is None or pe is None:
                continue

            # 2. SIGNAL LOGIC & AI ANALYSIS
            signal_type = None
            if ce > pe * 2:
                signal_type = "PE"
                entry = row.get("PE_LTP", 0)
                st.error(f"🚨 {selected_idx} {strike} - PE SIGNAL FOUND")
            elif pe > ce * 2:
                signal_type = "CE"
                entry = row.get("CE_LTP", 0)
                st.success(f"🚀 {selected_idx} {strike} - CE SIGNAL FOUND")

            if signal_type:
                signals_found = True
                
                # Metrics Row
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("ENTRY", entry)
                c2.metric("SL (20%)", round(entry * 0.8, 2))
                c3.metric("TG1 (20%)", round(entry * 1.2, 2))
                c4.metric("TG2 (50%)", round(entry * 1.5, 2))
                
                # AI Analysis Explanation
                with st.expander(f"View AI Analysis for {strike} {signal_type}"):
                    if signal_type == "CE":
                        st.write(f"💡 **Analysis:** PE OI ({pe}) is significantly higher than CE OI ({ce}). This indicates strong support at {strike}. Bullish momentum expected.")
                    else:
                        st.write(f"💡 **Analysis:** CE OI ({ce}) is significantly higher than PE OI ({pe}). This indicates heavy resistance at {strike}. Bearish momentum expected.")
                st.divider()

        if not signals_found:
            st.info("No strong signals — showing data below")

        # 👉 ALWAYS SHOW TABLE
        st.subheader("📊 DATA TABLE")
        st.dataframe(df.set_index("Strike"), use_container_width=True)

except Exception as e:
    st.error("⚠️ Error in signals section")
    st.exception(e)
