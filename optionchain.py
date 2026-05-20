# ---------------------------------------------------------
# TAB 2: ROBUST ADAPTIVE OPTION CHAIN ANALYZER (WITH MANUAL OVERRIDE)
# ---------------------------------------------------------
with tab2:
    st.header("📂 INSTITUTIONAL OPTION CHAIN ANALYZER")
    st.write("Upload an official NSE option chain spreadsheet file (CSV or Excel Format).")

    uploaded_file = st.file_uploader(
        "DROP DERIVATIVES DATA SHEET",
        type=["csv", "xlsx", "xls"]
    )

    if uploaded_file is not None:
        try:
            raw_df = None
            
            if uploaded_file.name.endswith(".csv"):
                for enc in ["utf-8", "latin-1", "cp1252"]:
                    try:
                        uploaded_file.seek(0)
                        raw_df = pd.read_csv(uploaded_file, engine='python', encoding=enc, on_bad_lines='skip')
                        break
                    except:
                        continue
            else:
                raw_df = pd.read_excel(uploaded_file, engine="openpyxl")

            if raw_df is not None and not raw_df.empty:
                raw_df.dropna(how='all', inplace=True)
                
                # Dynamic row header adjustment logic
                if not any(x in "".join(raw_df.columns.astype(str)).upper() for x in ["STRIKE", "OI", "VOLUME"]):
                    for i in range(min(10, len(raw_df))):  # Scans top 10 rows for headers
                        row_values = raw_df.iloc[i].astype(str).str.upper().tolist()
                        if any("STRIKE" in r or "OI" in r or "VOLUME" in r for r in row_values):
                            raw_df.columns = raw_df.iloc[i].astype(str).str.strip().str.upper()
                            raw_df = raw_df.iloc[i+1:].reset_index(drop=True)
                            break

                st.success("📊 SHEET INGESTED SUCCESSFULLY")
                
                # Clean column string modifications
                cols = [str(c).strip().upper() for c in raw_df.columns]
                raw_df.columns = cols

                # --- DEBUG WINDOW FOR USER ---
                st.info("🛠️ **DEBUG CONTROL PANEL:** If auto-detection fails, manually assign the columns below:")
                col1, col2, col3 = st.columns(3)
                
                # Auto-guessing columns for selectors
                guess_strike = next((c for c in cols if "STRIKE" in c or "STRK" in c), cols[len(cols)//2])
                oi_cols = [c for c in cols if "OI" in c or "OPEN INTEREST" in c]
                
                guess_call_oi = next((c for c in oi_cols if "CALL" in c or "CE" in c), oi_cols[0] if oi_cols else cols[0])
                guess_put_oi = next((c for c in oi_cols if "PUT" in c or "PE" in c), oi_cols[-1] if oi_cols else cols[-1])

                selected_strike_col = col1.selectbox("Select STRIKE PRICE Column", cols, index=cols.index(guess_strike))
                selected_call_oi = col2.selectbox("Select CALL OI Column", cols, index=cols.index(guess_call_oi))
                selected_put_oi = col3.selectbox("Select PUT OI Column", cols, index=cols.index(guess_put_oi))

                with st.expander("🔍 PREVIEW RAW DATA STRUCTURE"):
                    st.dataframe(raw_df.head(15), use_container_width=True)

                if st.button("🚀 EXECUTE DERIVATIVES VOLUME & OI QUANTS", use_container_width=True):
                    def clean_numeric(series):
                        return pd.to_numeric(series.astype(str).str.replace(',', '').str.strip(), errors='coerce').fillna(0)

                    if selected_strike_col and selected_call_oi and selected_put_oi:
                        strikes = clean_numeric(raw_df[selected_strike_col])
                        c_oi = clean_numeric(raw_df[selected_call_oi])
                        p_oi = clean_numeric(raw_df[selected_put_oi])
                        
                        # Filter out rows with zero strike or summary rows
                        valid_mask = (strikes > 0) & ((c_oi > 0) | (p_oi > 0))
                        strikes = strikes[valid_mask]
                        c_oi = c_oi[valid_mask]
                        p_oi = p_oi[valid_mask]

                        total_call_oi = c_oi.sum()
                        total_put_oi = p_oi.sum()
                        
                        pcr = total_put_oi / total_call_oi if total_call_oi > 0 else 1.0

                        # Locate support & resistance
                        resistance_wall = strikes.iloc[c_oi.idxmax()] if not c_oi.empty else 0
                        support_wall = strikes.iloc[p_oi.idxmax()] if not p_oi.empty else 0

                        if pcr >= 1.15:
                            chain_signal = "🚀 BULLISH MOMENTUM (Strong Put Writing Support)"
                            color_alert = st.success
                        elif pcr <= 0.80:
                            chain_signal = "🔻 BEARISH MOMENTUM (Aggressive Call Overwriting)"
                            color_alert = st.error
                        else:
                            chain_signal = "⚠️ RANGEBOUND / NEUTRAL MIXED MOMENTUM"
                            color_alert = st.warning

                        st.subheader("🤖 OPTION CHAIN DERIVATIVE MATRIX ANALYSIS")
                        color_alert(f"🎯 AI DERIVATIVE PROFILE DIRECTION: {chain_signal}")

                        a1, a2, a3, a4 = st.columns(4)
                        a1.metric("PUT-CALL RATIO (PCR)", round(pcr, 3))
                        a2.metric("LIQUID OPEN INTEREST SUPPORT (MAX PUT OI)", f"₹ {int(support_wall) if support_wall > 0 else 'N/A'}")
                        a3.metric("LIQUID OPEN INTEREST RESISTANCE (MAX CALL OI)", f"₹ {int(resistance_wall) if resistance_wall > 0 else 'N/A'}")
                        a4.metric("TOTAL OPEN INTEREST CONTRACTS", f"{int(total_call_oi + total_put_oi):,}")

                        # Chart Rendering
                        fig_chain = go.Figure()
                        fig_chain.add_trace(go.Bar(x=strikes, y=c_oi, name='Call OI (Resistance)', marker_color='#EF4444'))
                        fig_chain.add_trace(go.Bar(x=strikes, y=p_oi, name='Put OI (Support)', marker_color='#10B981'))
                        
                        fig_chain.update_layout(
                            template="plotly_dark",
                            barmode='group',
                            height=450,
                            title="REAL-TIME OPEN INTEREST CONCENTRIC WALLS BY STRIKE PRICE",
                            xaxis_title="Strike Price Target",
                            yaxis_title="Open Interest Contracts Stack",
                            paper_bgcolor="#0E1117",
                            plot_bgcolor="#0E1117"
                        )
                        st.plotly_chart(fig_chain, use_container_width=True)
                    else:
                        st.error("❌ Column selection missing. Please select correct columns from the dropdown choices above.")
            else:
                st.error("❌ FILE FORMAT REJECTION: Matrix processing system returned blank rows on initialization.")
        except Exception as e:
            st.error(f"🔴 DERIVATIVE CALCULATION SPREAD EXCEPTION ERROR: {str(e)}")
