"""
Liquidity Engine - Partner Draws
Track personal draws between Mark & Katie from the business
"""
import streamlit as st
import pandas as pd
from datetime import date, datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import config
from utils import database as db
from utils.auth import require_auth

st.set_page_config(
    page_title="Partner Draws | Liquidity Engine",
    page_icon="👫",
    layout="wide"
)

require_auth()

st.title("👫 Partner Draws")
st.caption("Track personal draws from the business between Mark & Katie")

# Get totals
totals = db.get_partner_totals()
mark_total = totals.get('Mark', 0)
katie_total = totals.get('Katie', 0)
difference = mark_total - katie_total

# Summary metrics
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Mark's Total", 
        f"${mark_total:,.2f}", 
        f"{totals.get('Mark_count', 0)} entries"
    )

with col2:
    st.metric(
        "Katie's Total", 
        f"${katie_total:,.2f}",
        f"{totals.get('Katie_count', 0)} entries"
    )

with col3:
    if difference > 0:
        st.metric("Difference", f"${abs(difference):,.2f}", "Mark ahead", delta_color="inverse")
    elif difference < 0:
        st.metric("Difference", f"${abs(difference):,.2f}", "Katie ahead", delta_color="inverse")
    else:
        st.metric("Difference", "$0.00", "Even")

st.divider()

# Tabs
tab1, tab2, tab3 = st.tabs(["📋 All Draws", "➕ Add Draw", "📥 Import from Excel"])

# ============ TAB 1: View All Draws ============
with tab1:
    # Filters
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        filter_partner = st.selectbox("Filter by Partner", ["All", "Mark", "Katie"])
    with col2:
        sort_order = st.selectbox("Sort", ["Newest First", "Oldest First", "Amount (High)", "Amount (Low)"])
    
    # Get draws
    partner_filter = None if filter_partner == "All" else filter_partner
    draws = db.get_partner_draws(partner=partner_filter)
    
    if draws:
        # Side by side view
        st.markdown("### Draw History")
        
        mark_draws = [d for d in draws if d['partner'] == 'Mark'] if filter_partner != "Katie" else []
        katie_draws = [d for d in draws if d['partner'] == 'Katie'] if filter_partner != "Mark" else []
        
        col1, col2 = st.columns(2)
        
        def format_amount(x):
            if x < 0:
                return f"(${abs(x):,.2f})"  # Credits/returns in parentheses
            return f"${x:,.2f}"
        
        with col1:
            st.markdown("#### 👨 Mark")
            if mark_draws:
                mark_df = pd.DataFrame([{
                    'Date': d['draw_date'],
                    'Description': d['description'],
                    'Amount': d['amount'],
                    'Notes': d['notes'] or ''
                } for d in mark_draws])
                
                mark_df['Amount'] = mark_df['Amount'].apply(format_amount)
                st.dataframe(mark_df, use_container_width=True, hide_index=True)
            else:
                st.info("No draws for Mark")
        
        with col2:
            st.markdown("#### 👩 Katie")
            if katie_draws:
                katie_df = pd.DataFrame([{
                    'Date': d['draw_date'],
                    'Description': d['description'],
                    'Amount': d['amount'],
                    'Notes': d['notes'] or ''
                } for d in katie_draws])
                
                katie_df['Amount'] = katie_df['Amount'].apply(format_amount)
                st.dataframe(katie_df, use_container_width=True, hide_index=True)
            else:
                st.info("No draws for Katie")
        
        # Full list with edit/delete options
        st.divider()
        st.markdown("### Manage Entries")
        
        for draw in draws[:50]:  # Limit display
            with st.expander(f"{draw['partner']} | {draw['draw_date']} | {draw['description']} | ${draw['amount']:,.2f}"):
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.markdown(f"**Partner:** {draw['partner']}")
                    st.markdown(f"**Date:** {draw['draw_date']}")
                    st.markdown(f"**Description:** {draw['description']}")
                    st.markdown(f"**Amount:** ${draw['amount']:,.2f}")
                    if draw['notes']:
                        st.markdown(f"**Notes:** {draw['notes']}")
                with col3:
                    if st.button("🗑️ Delete", key=f"del_{draw['id']}"):
                        db.delete_partner_draw(draw['id'])
                        st.success("Deleted!")
                        st.rerun()
    else:
        st.info("No draws recorded yet. Add draws or import from Excel.")

# ============ TAB 2: Add Draw ============
with tab2:
    st.markdown("### Add New Draw Entry")
    
    with st.form("add_draw_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            partner = st.selectbox("Partner", ["Mark", "Katie"])
            draw_date = st.date_input("Date", value=date.today())
            description = st.text_input("Description", placeholder="e.g., Nordstrom, Dinner at Nobu")
        
        with col2:
            amount = st.number_input("Amount", value=0.0, step=10.0, 
                                      help="Positive = expense, Negative = return/credit")
            notes = st.text_input("Notes (optional)", placeholder="e.g., Birthday gift, Return")
        
        is_return = st.checkbox("This is a return/credit (will make amount negative)")
        
        submitted = st.form_submit_button("Add Draw", type="primary")
        
        if submitted:
            if not description:
                st.error("Please enter a description")
            else:
                final_amount = -abs(amount) if is_return else abs(amount)
                db.add_partner_draw(
                    partner=partner,
                    draw_date=draw_date.isoformat(),
                    description=description,
                    amount=final_amount,
                    notes=notes if notes else None
                )
                st.success(f"Added ${abs(final_amount):,.2f} {'credit' if is_return else 'draw'} for {partner}!")
                st.rerun()

# ============ TAB 3: Import from Excel ============
with tab3:
    st.markdown("### Import from Excel")
    st.caption("Import draws from your MK_Private.xlsx file")
    
    st.warning("⚠️ Importing will **replace** all existing draw entries!")
    
    uploaded_file = st.file_uploader("Upload MK_Private.xlsx", type=['xlsx'])
    
    if uploaded_file:
        # Save uploaded file temporarily
        temp_path = Path("/tmp/mk_private_upload.xlsx")
        temp_path.write_bytes(uploaded_file.getvalue())
        
        # Preview the file
        try:
            df = pd.read_excel(temp_path, sheet_name='Draw 2025', header=None)
            
            st.markdown("#### Preview")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Katie's Entries (first 10)**")
                katie_preview = df.iloc[1:11, [0, 1, 2, 3]].copy()
                katie_preview.columns = ['Date', 'Description', 'Amount', 'Notes']
                st.dataframe(katie_preview, hide_index=True)
            
            with col2:
                st.markdown("**Mark's Entries (first 10)**")
                mark_preview = df.iloc[1:11, [5, 6, 7]].copy()
                mark_preview.columns = ['Date', 'Description', 'Amount']
                st.dataframe(mark_preview, hide_index=True)
            
            # Count entries
            katie_count = df.iloc[1:, 2].notna().sum()
            mark_count = df.iloc[1:, 7].notna().sum()
            
            st.info(f"Found approximately **{katie_count}** entries for Katie and **{mark_count}** entries for Mark")
            
            if st.button("🚀 Import All Draws", type="primary"):
                try:
                    results = db.import_partner_draws_from_excel(str(temp_path))
                    st.success(f"✅ Imported {results['Katie']} entries for Katie and {results['Mark']} entries for Mark!")
                    st.balloons()
                    st.rerun()
                except Exception as e:
                    st.error(f"Import failed: {str(e)}")
        
        except Exception as e:
            st.error(f"Could not read file: {str(e)}")

# Sidebar summary
with st.sidebar:
    st.markdown("### 💰 Draw Summary")
    st.markdown(f"**Mark:** ${mark_total:,.2f}")
    st.markdown(f"**Katie:** ${katie_total:,.2f}")
    
    st.divider()
    
    if difference > 0:
        st.markdown(f"Mark has drawn **${abs(difference):,.2f}** more")
    elif difference < 0:
        st.markdown(f"Katie has drawn **${abs(difference):,.2f}** more")
    else:
        st.markdown("Draws are **even**")
    
    st.divider()
    
    st.caption("Negative amounts = returns/credits")
