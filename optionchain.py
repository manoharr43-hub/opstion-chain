# ===============================
# SIGNALS + TABLE (FIXED)
# ===============================
st.subheader("🔥 AI SIGNALS")

try:
    if df is None or df.empty:
        st.warning("⚠️ No data available")
    else:
        signals_found = False

        for _, row in df.iterrows():
            ce = row.get("CE_OI", 0)
            pe = row.get("PE_OI", 0)

            # SAFE CHECK
            if ce is None or pe is None:
                continue

            if ce > pe * 2:
                signals_found = True
                entry = row.get("PE_LTP", 0)
                st.error(f"{selected_idx} {row['Strike']} PE SIGNAL")

                c1, c2, c3, c4 = st.columns(4)
                c1.metric("ENTRY", entry)
                c2.metric("SL", round(entry * 0.8, 2))
                c3.metric("TG1", round(entry * 1.2, 2))
                c4.metric("TG2", round(entry * 1.5, 2))

            elif pe > ce * 2:
                signals_found = True
                entry = row.get("CE_LTP", 0)
                st.success(f"{selected_idx} {row['Strike']} CE SIGNAL")

                c1, c2, c3, c4 = st.columns(4)
                c1.metric("ENTRY", entry)
                c2.metric("SL", round(entry * 0.8, 2))
                c3.metric("TG1", round(entry * 1.2, 2))
                c4.metric("TG2", round(entry * 1.5, 2))

        # 👉 fallback message
        if not signals_found:
            st.info("No strong signals — showing data below")

        # 👉 ALWAYS SHOW TABLE
        st.subheader("📊 DATA TABLE")
        st.dataframe(df.set_index("Strike"), use_container_width=True)

except Exception as e:
    st.error("⚠️ Error in signals section")
    st.write(e)
