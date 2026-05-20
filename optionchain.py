# =========================================================
# TAB 2: OPTION CHAIN ANALYZER (BULLETPROOF PARSER)
# =========================================================
with tab2:
    st.header("📂 INSTITUTIONAL OPTION CHAIN ANALYZER")
    st.write("Upload official NSE option chain file (CSV / Excel).")

    uploaded_file = st.file_uploader("DROP FILE HERE", type=["csv", "xlsx", "xls"])

    if uploaded_file is not None:
        try:
            # Read purely without assuming headers to bypass pandas duplicate column merging
            if uploaded_file.name.endswith(".csv"):
                raw_df = pd.read_csv(uploaded_file, engine='python', on_bad_lines='skip', header=None)
            else:
                raw_df = pd.read_excel(uploaded_file, header=None)

            if raw_df is not None and not raw_df.empty:
                raw_df.dropna(how='all', inplace=True)

                # Find the actual row that contains the words STRIKE and OI
                header_idx = 0
                for i in range(min(15, len(raw_df))):
                    # FIX: Safely convert every single cell to a string before joining to prevent Float/NaN errors
                    row_values = [str(val) for val in raw_df.iloc[i].values]
                    row_text = " ".join(row_values).upper()
                    
                    if "STRIKE" in row_text and "OI" in row_text:
                        header_idx = i
                        break
                
                # Extract headers and data body (Safely convert all headers to string)
                raw_headers = [str(val).strip().upper() for val in raw_df.iloc[header_idx].values]
                data_df = raw_df.iloc[header_idx+1:].copy().reset_index(drop=True)
                data_df.dropna(how='all', inplace=True)

                # Locate center STRIKE point to split CALLS and PUTS
                strike_pos = next((i for i, h in enumerate(raw_headers) if "STRIKE" in h or "STRK" in h), len(raw_headers)//2)

                # Rename columns physically to prevent mixing
                final_columns = []
                for i, col in enumerate(raw_headers):
                    col = col.replace(" ", "_").replace(".", "")
                    if col in ['NAN', 'NONE', '']: 
                        col = f"DATA_{i}"

                    if i < strike_pos: final_columns.append(f"CALL_{col}")
                    elif i > strike_pos: final_columns.append(f"PUT_{col}")
                    else: final_columns.append("STRIKE_PRICE")

                data_df.columns = final_columns
                st.success("📊 NSE DATA DETECTED & STRUCTURED")
                
                # Column selection UI
                st.info("🛠️ **MAPPING ENGINE:** Left side mapped as CALLS, Right side mapped as PUTS.")
                col1, col2, col3 = st.columns(3)
                cols = list(data_df.columns)
                
                guess_strike = "STRIKE_PRICE" if "STRIKE_PRICE" in cols else cols[0]
                guess_call_oi = next((c for c in cols if c == "CALL_OI" or "CALL_CHNG_IN_OI" in c), cols[0])
                guess_put_oi = next((c for c in cols if c == "PUT_OI" or "PUT_CHNG_IN_OI" in c), cols[-1])

                selected_strike = col1.selectbox("STRIKE PRICE Column", cols, index=cols.index(guess_strike) if guess_strike in cols else 0)
                selected_call = col2.selectbox("CALL OI Column", cols, index=cols.index(guess_call_oi) if guess_call_oi in cols else 0)
                selected_put = col3.selectbox("PUT OI Column", cols, index=cols.index(guess_put_oi) if guess_put_oi in cols else 0)

                with st.expander("🔍 VIEW CLEANED MATRIX DATA"):
                    st.dataframe(data_df.head(10), use_container_width=True)

                # Execution Engine
                if st.button("🚀 EXECUTE AI QUANTS", use_container_width=True):
                    def clean_num(series):
                        return pd.to_numeric(series.astype(str).str.replace(',', '').str.strip(), errors='coerce').fillna(0)

                    if selected_strike and selected_call and selected_put:
                        strikes = clean_num(data_df[selected_strike])
                        c_oi = clean_num(data_df[selected_call])
                        p_oi = clean_num(data_df[selected_put])
                        
                        # Filter out empty/total rows at the bottom
                        valid_mask = (strikes > 0) & ((c_oi > 0) | (p_oi > 0))
                        strikes, c_oi, p_oi = strikes[valid_mask], c_oi[valid_mask], p_oi[valid_mask]

                        total_c_oi = c_oi.sum()
                        total_p_oi = p_oi.sum()
                        pcr = total_p_oi / total_c_oi if total_c_oi > 0 else 1.0

                        resistance = strikes.iloc[c_oi.idxmax()] if not c_oi.empty else 0
                        support = strikes.iloc[p_oi.idxmax()] if not p_oi.empty else 0

                        if pcr >= 1.15: signal, color = "🚀 BULLISH (Strong Put Support)", st.success
                        elif pcr <= 0.85: signal, color = "🔻 BEARISH (Call Overwriting)", st.error
                        else: signal, color = "⚠️ RANGEBOUND / NEUTRAL", st.warning

                        st.subheader("🤖 DERIVATIVE MATRIX REPORT")
                        color(f"🎯 DIRECTION: {signal}")

                        m1, m2, m3, m4 = st.columns(4)
                        m1.metric("PUT-CALL RATIO (PCR)", round(pcr, 2))
                        m2.metric("SUPPORT (MAX PUT OI)", f"₹ {int(support)}")
                        m3.metric("RESISTANCE (MAX CALL OI)", f"₹ {int(resistance)}")
                        m4.metric("TOTAL OPEN CONTRACTS", f"{int(total_c_oi + total_p_oi):,}")

                        # Bar Chart
                        fig_bar = go.Figure()
                        fig_bar.add_trace(go.Bar(x=strikes, y=c_oi, name='Call OI (Resistance)', marker_color='#EF4444'))
                        fig_bar.add_trace(go.Bar(x=strikes, y=p_oi, name='Put OI (Support)', marker_color='#10B981'))
                        fig_bar.update_layout(template="plotly_dark", barmode='group', height=450, title="OPEN INTEREST WALLS", xaxis_title="Strike Price", yaxis_title="OI Contracts")
                        st.plotly_chart(fig_bar, use_container_width=True)
                    else:
                        st.error("❌ Missing required columns.")
        except Exception as e:
            st.error(f"🔴 DATA PARSING ERROR: {str(e)}")
