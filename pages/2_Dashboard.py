"""
Liquidity Engine - Dashboard (The Pulse)
Mobile-friendly financial overview
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import config
from utils import database as db
from utils.auth import require_auth

st.set_page_config(page_title="Dashboard | Liquidity Engine", page_icon="📊", layout="wide")

require_auth()

# Custom CSS for mobile-friendly compact display
st.markdown("""
<style>
    /* Compact metrics */
    [data-testid="stMetricValue"] { font-size: 1.2rem !important; }
    [data-testid="stMetricLabel"] { font-size: 0.8rem !important; }
    
    /* Tighter spacing */
    .block-container { padding: 1rem !important; }
    
    /* Smaller headers */
    h1 { font-size: 1.5rem !important; }
    h2 { font-size: 1.2rem !important; }
    h3 { font-size: 1rem !important; }
    
    /* Compact expanders */
    .streamlit-expanderHeader { font-size: 0.9rem !important; padding: 0.5rem !important; }
    
    /* Compact tables */
    .stDataFrame { font-size: 0.8rem !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("## 📊 Dashboard")

# Get all accounts
accounts = db.get_all_accounts()

# Calculate totals by type
debt_by_type = {}
credit_cards = []
for acc in accounts:
    acc_type = acc['account_type']
    balance = acc['current_balance']
    
    if acc_type not in debt_by_type:
        debt_by_type[acc_type] = {'total': 0, 'accounts': []}
    debt_by_type[acc_type]['total'] += balance
    debt_by_type[acc_type]['accounts'].append(acc)
    
    if acc_type == 'credit_card':
        credit_cards.append(acc)

total_debt = sum(d['total'] for d in debt_by_type.values())
total_payments = sum(acc['minimum_payment'] or 0 for acc in accounts)

# Credit card totals
cc_balance = sum(acc['current_balance'] for acc in credit_cards)
cc_limit = sum(acc['credit_limit'] or 0 for acc in credit_cards)
cc_available = cc_limit - cc_balance
cc_utilization = (cc_balance / cc_limit * 100) if cc_limit > 0 else 0

# Partner draw totals
draw_totals = db.get_partner_totals()

# ============ TOP METRICS (compact) ============
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Debt", f"${total_debt/1000:.0f}K")
with col2:
    st.metric("Due This Month", f"${total_payments/1000:.0f}K")
with col3:
    st.metric("CC Available", f"${cc_available/1000:.0f}K")

st.divider()

# ============ CREDIT CARDS (collapsible with details) ============
with st.expander(f"💳 Credit Cards: ${cc_balance:,.0f} / ${cc_limit:,.0f} ({cc_utilization:.0f}% used)", expanded=True):
    for acc in credit_cards:
        limit = acc['credit_limit'] or 0
        balance = acc['current_balance']
        available = limit - balance if limit > 0 else 0
        util = (balance / limit * 100) if limit > 0 else 0
        payment = acc['minimum_payment'] or 0
        due = acc['due_day'] or '-'
        
        # Color code utilization
        if util > 90:
            color = "🔴"
        elif util > 70:
            color = "🟡"
        else:
            color = "🟢"
        
        c1, c2, c3 = st.columns([3, 2, 1])
        with c1:
            st.markdown(f"**{acc['name'][:20]}**")
        with c2:
            st.markdown(f"{color} ${balance:,.0f} / ${limit:,.0f}")
        with c3:
            if payment > 0:
                st.markdown(f"Due {due}: ${payment:,.0f}")

# ============ LOANS BY TYPE (collapsible) ============
loan_types = {
    'private_loan': ('🤝 Private Loans', 'private_loan'),
    'personal_loan': ('💰 Personal Loans', 'personal_loan'),
    'auto_loan': ('🚗 Auto Loan', 'auto_loan'),
    'tax_debt': ('🏛️ Tax Debt', 'tax_debt'),
}

for loan_type, (label, key) in loan_types.items():
    if key in debt_by_type:
        data = debt_by_type[key]
        with st.expander(f"{label}: ${data['total']:,.0f}", expanded=False):
            for acc in data['accounts']:
                payment = acc['minimum_payment'] or 0
                due = acc['due_day'] or '-'
                c1, c2 = st.columns([3, 2])
                with c1:
                    st.markdown(f"**{acc['name'][:25]}**")
                with c2:
                    if payment > 0:
                        st.markdown(f"${acc['current_balance']:,.0f} • Due {due}: ${payment:,.0f}")
                    else:
                        st.markdown(f"${acc['current_balance']:,.0f}")

st.divider()

# ============ PARTNER DRAWS (compact) ============
with st.expander(f"👫 Partner Draws: Mark ${draw_totals['Mark']:,.0f} | Katie ${draw_totals['Katie']:,.0f}", expanded=True):
    diff = draw_totals['Mark'] - draw_totals['Katie']
    if diff > 0:
        st.markdown(f"**Mark ahead by ${diff:,.2f}**")
    elif diff < 0:
        st.markdown(f"**Katie ahead by ${abs(diff):,.2f}**")
    else:
        st.markdown("**Even**")
    
    # Mini bar chart
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[draw_totals['Mark'], draw_totals['Katie']],
        y=['Mark', 'Katie'],
        orientation='h',
        marker_color=['#4CAF50', '#E91E63']
    ))
    fig.update_layout(
        height=100,
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
        xaxis=dict(showticklabels=False),
        yaxis=dict(showticklabels=True),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig, use_container_width=True)

# ============ REWARDS POINTS (compact) ============
rewards = db.get_rewards_points()
total_value = sum(r['current_balance'] * r['point_value'] for r in rewards)

with st.expander(f"✨ Rewards: ${total_value:,.0f} value", expanded=False):
    for r in rewards:
        value = r['current_balance'] * r['point_value']
        st.markdown(f"**{r['program_name'][:20]}**: {r['current_balance']:,} pts (${value:,.0f})")

# ============ QUICK ACTIONS ============
st.divider()
st.markdown("### Quick Actions")
c1, c2, c3 = st.columns(3)
with c1:
    if st.button("📋 Accounts", use_container_width=True):
        st.switch_page("pages/1_Accounts.py")
with c2:
    if st.button("👫 Draws", use_container_width=True):
        st.switch_page("pages/8_Partner_Draws.py")
with c3:
    if st.button("⚙️ Settings", use_container_width=True):
        st.switch_page("pages/7_Settings.py")
