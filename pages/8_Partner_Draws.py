"""
Liquidity Engine - Partner Draws
Track personal draws between Mark & Katie from the business
Mobile-friendly with full transaction history
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

# Custom CSS for compact mobile display
st.markdown("""
<style>
    [data-testid="stMetricValue"] { font-size: 1.1rem !important; }
    [data-testid="stMetricLabel"] { font-size: 0.75rem !important; }
    .block-container { padding: 1rem !important; }
    h1 { font-size: 1.4rem !important; }
    h2 { font-size: 1.1rem !important; }
    .stDataFrame { font-size: 0.75rem !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("## 👫 Partner Draws")

# Get totals
totals = db.get_partner_totals()
diff = totals['Mark'] - totals['Katie']

# ============ SUMMARY METRICS ============
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Mark", f"${totals['Mark']:,.0f}", f"{totals['Mark_count']} items")
with col2:
    st.metric("Katie", f"${totals['Katie']:,.0f}", f"{totals['Katie_count']} items")
with col3:
    if diff > 0:
        st.metric("Balance", f"Mark +${diff:,.0f}")
    elif diff < 0:
        st.metric("Balance", f"Katie +${abs(diff):,.0f}")
    else:
        st.metric("Balance", "Even")

st.divider()

# ============ ADD NEW DRAW ============
with st.expander("➕ Add New Draw", expanded=False):
    with st.form("new_draw"):
        c1, c2 = st.columns(2)
        with c1:
            partner = st.selectbox("Partner", ["Mark", "Katie"])
            draw_date = st.date_input("Date", value=date.today())
        with c2:
            amount = st.number_input("Amount", min_value=-10000.0, max_value=50000.0, value=0.0, step=0.01)
            description = st.text_input("Description")
        
        category = st.selectbox("Category", ["Shopping", "Dining", "Travel", "Entertainment", "Health", "Gifts", "Other"])
        notes = st.text_input("Notes (optional)")
        
        if st.form_submit_button("Add Draw", use_container_width=True):
            if description and amount != 0:
                db.add_partner_draw(partner, draw_date.isoformat(), description, amount, f"{category}: {notes}" if notes else category)
                st.success(f"Added ${amount:,.2f} for {partner}")
                st.rerun()
            else:
                st.error("Enter description and amount")

st.divider()

# ============ TRANSACTION FILTERS ============
col1, col2, col3 = st.columns(3)
with col1:
    filter_partner = st.selectbox("Filter", ["All", "Mark", "Katie"], key="partner_filter")
with col2:
    sort_order = st.selectbox("Sort", ["Newest First", "Oldest First", "Highest Amount", "Lowest Amount"], key="sort")
with col3:
    search = st.text_input("Search", placeholder="Description...", key="search")

# ============ TRANSACTION LIST ============
# Get all draws
with db.get_connection() as conn:
    cursor = conn.cursor()
    
    query = "SELECT * FROM partner_draws WHERE 1=1"
    params = []
    
    if filter_partner != "All":
        query += " AND partner = ?"
        params.append(filter_partner)
    
    if search:
        query += " AND description LIKE ?"
        params.append(f"%{search}%")
    
    # Sort
    if sort_order == "Newest First":
        query += " ORDER BY draw_date DESC, id DESC"
    elif sort_order == "Oldest First":
        query += " ORDER BY draw_date ASC, id ASC"
    elif sort_order == "Highest Amount":
        query += " ORDER BY amount DESC"
    else:
        query += " ORDER BY amount ASC"
    
    cursor.execute(query, params)
    draws = cursor.fetchall()

# Display count
st.caption(f"Showing {len(draws)} transactions")

# Create tabs for Mark and Katie views
if filter_partner == "All":
    tab1, tab2 = st.tabs(["📋 All Transactions", "📊 Side by Side"])
    
    with tab1:
        # Display as compact list
        for draw in draws:
            emoji = "🔵" if draw['partner'] == 'Mark' else "🔴"
            amount = draw['amount']
            amt_str = f"${amount:,.2f}" if amount >= 0 else f"-${abs(amount):,.2f}"
            color = "" if amount >= 0 else "~~"
            
            c1, c2, c3 = st.columns([1, 4, 2])
            with c1:
                st.markdown(f"{emoji}")
            with c2:
                st.markdown(f"**{draw['description'][:30]}**")
                st.caption(f"{draw['draw_date']}")
            with c3:
                st.markdown(f"**{amt_str}**")
    
    with tab2:
        # Side by side comparison
        mark_draws = [d for d in draws if d['partner'] == 'Mark']
        katie_draws = [d for d in draws if d['partner'] == 'Katie']
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### Mark")
            for d in mark_draws[:50]:  # Show first 50
                amt = d['amount']
                st.markdown(f"${amt:,.0f} - {d['description'][:20]}")
            if len(mark_draws) > 50:
                st.caption(f"+ {len(mark_draws) - 50} more...")
        
        with c2:
            st.markdown("### Katie")
            for d in katie_draws[:50]:
                amt = d['amount']
                st.markdown(f"${amt:,.0f} - {d['description'][:20]}")
            if len(katie_draws) > 50:
                st.caption(f"+ {len(katie_draws) - 50} more...")

else:
    # Single partner view - show all transactions
    st.markdown(f"### {filter_partner}'s Draws")
    
    for draw in draws:
        amount = draw['amount']
        amt_str = f"${amount:,.2f}" if amount >= 0 else f"-${abs(amount):,.2f}"
        
        c1, c2 = st.columns([3, 1])
        with c1:
            st.markdown(f"**{draw['description']}**")
            st.caption(f"{draw['draw_date']} {draw['notes'] or ''}")
        with c2:
            if amount >= 0:
                st.markdown(f"**{amt_str}**")
            else:
                st.markdown(f"*{amt_str}* (return)")

# ============ IMPORT SECTION ============
st.divider()
with st.expander("📤 Import from Excel", expanded=False):
    st.markdown("""
    Upload an Excel file with partner draws.
    Expected format: Katie in columns A-D, Mark in columns F-H
    """)
    
    uploaded_file = st.file_uploader("Choose Excel file", type=['xlsx', 'xls'])
    
    if uploaded_file:
        if st.button("Import Draws", type="primary"):
            # Save temp file
            temp_path = Path("/tmp/draws_import.xlsx")
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            results = db.import_partner_draws_from_excel(str(temp_path))
            st.success(f"Imported: Mark ({results['Mark']}), Katie ({results['Katie']})")
            st.rerun()

# ============ EXPORT SECTION ============
with st.expander("📥 Export Data", expanded=False):
    if st.button("Download as CSV"):
        with db.get_connection() as conn:
            df = pd.read_sql_query("SELECT partner, draw_date, description, amount, notes FROM partner_draws ORDER BY draw_date DESC", conn)
        
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="partner_draws.csv",
            mime="text/csv"
        )
