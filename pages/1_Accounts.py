"""
Liquidity Engine - Accounts Management
Mobile-friendly with credit limits display
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
    page_title="Accounts | Liquidity Engine",
    page_icon="💳",
    layout="wide"
)

require_auth()

# Custom CSS for mobile-friendly compact display
st.markdown("""
<style>
    [data-testid="stMetricValue"] { font-size: 1.1rem !important; }
    [data-testid="stMetricLabel"] { font-size: 0.75rem !important; }
    .block-container { padding: 1rem !important; }
    h1 { font-size: 1.4rem !important; }
    h2 { font-size: 1.1rem !important; }
    h3 { font-size: 1rem !important; }
    .streamlit-expanderHeader { font-size: 0.85rem !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("## 💳 Accounts")

# Get all accounts
accounts = db.get_all_accounts()

# Calculate totals
total_debt = sum(acc['current_balance'] for acc in accounts)
total_payments = sum(acc['minimum_payment'] or 0 for acc in accounts)

# Credit card stats
credit_cards = [acc for acc in accounts if acc['account_type'] == 'credit_card']
cc_balance = sum(acc['current_balance'] for acc in credit_cards)
cc_limit = sum(acc['credit_limit'] or 0 for acc in credit_cards)
cc_available = cc_limit - cc_balance

# ============ SUMMARY METRICS ============
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Debt", f"${total_debt:,.0f}")
with col2:
    st.metric("Payments Due", f"${total_payments:,.0f}")
with col3:
    st.metric("CC Available", f"${cc_available:,.0f}")

st.divider()

# ============ FILTER ============
filter_type = st.selectbox("Filter by Type", ["All", "Credit Cards", "Personal Loans", "Private Loans", "Auto Loan", "Tax Debt"])

# Filter accounts
if filter_type == "Credit Cards":
    filtered = [a for a in accounts if a['account_type'] == 'credit_card']
elif filter_type == "Personal Loans":
    filtered = [a for a in accounts if a['account_type'] == 'personal_loan']
elif filter_type == "Private Loans":
    filtered = [a for a in accounts if a['account_type'] == 'private_loan']
elif filter_type == "Auto Loan":
    filtered = [a for a in accounts if a['account_type'] == 'auto_loan']
elif filter_type == "Tax Debt":
    filtered = [a for a in accounts if a['account_type'] == 'tax_debt']
else:
    filtered = accounts

# ============ ACCOUNTS LIST ============
for acc in filtered:
    balance = acc['current_balance']
    payment = acc['minimum_payment'] or 0
    due = acc['due_day'] or '-'
    limit = acc['credit_limit']
    
    # Build header
    header = f"{acc['name']}"
    if acc['account_type'] == 'credit_card' and limit:
        available = limit - balance
        util = (balance / limit * 100) if limit > 0 else 0
        if util > 90:
            emoji = "🔴"
        elif util > 70:
            emoji = "🟡"
        else:
            emoji = "🟢"
        header = f"{emoji} {acc['name']} | ${balance:,.0f} / ${limit:,.0f}"
    else:
        header = f"📄 {acc['name']} | ${balance:,.0f}"
    
    with st.expander(header, expanded=False):
        # Account details in compact format
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown(f"**Institution:** {acc['institution']}")
            st.markdown(f"**Type:** {acc['account_type'].replace('_', ' ').title()}")
            st.markdown(f"**Balance:** ${balance:,.2f}")
            if limit:
                st.markdown(f"**Credit Limit:** ${limit:,.0f}")
                st.markdown(f"**Available:** ${limit - balance:,.0f}")
        
        with c2:
            st.markdown(f"**Payment Due:** ${payment:,.2f}")
            st.markdown(f"**Due Day:** {due}")
            st.markdown(f"**Business:** {'✅' if acc['is_business'] else '❌'}")
            if acc['notes']:
                st.markdown(f"**Notes:** {acc['notes']}")
        
        # Quick update
        st.divider()
        st.markdown("**Quick Update**")
        c1, c2 = st.columns(2)
        with c1:
            new_balance = st.number_input(
                "New Balance",
                value=float(balance),
                key=f"bal_{acc['id']}",
                format="%.2f"
            )
        with c2:
            if st.button("Update", key=f"upd_{acc['id']}", use_container_width=True):
                db.update_account_balance(acc['id'], new_balance)
                st.success("Updated!")
                st.rerun()

# ============ REWARDS POINTS ============
st.divider()
st.markdown("### ✨ Rewards Points")

rewards = db.get_all_rewards()
total_value = sum(r['current_balance'] * r['point_value'] for r in rewards)
st.caption(f"Total Value: ${total_value:,.0f}")

for r in rewards:
    value = r['current_balance'] * r['point_value']
    with st.expander(f"{r['program_name']}: {r['current_balance']:,} pts (${value:,.0f})", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            new_balance = st.number_input(
                "Update Points",
                value=r['current_balance'],
                key=f"rwd_{r['id']}",
                step=100
            )
        with c2:
            if st.button("Update", key=f"rwd_upd_{r['id']}", use_container_width=True):
                db.update_rewards_balance_by_id(r['id'], new_balance)
                st.success("Updated!")
                st.rerun()

# ============ ADD ACCOUNT ============
st.divider()
with st.expander("➕ Add New Account", expanded=False):
    with st.form("new_account"):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Account Name")
            institution = st.text_input("Institution")
            account_type = st.selectbox("Type", ["credit_card", "personal_loan", "private_loan", "auto_loan", "tax_debt"])
        with c2:
            balance = st.number_input("Current Balance", value=0.0, format="%.2f")
            credit_limit = st.number_input("Credit Limit (if applicable)", value=0.0, format="%.2f")
            payment = st.number_input("Payment Due", value=0.0, format="%.2f")
        
        c1, c2 = st.columns(2)
        with c1:
            due_day = st.number_input("Due Day", min_value=1, max_value=31, value=15)
            is_business = st.checkbox("Business Account")
        with c2:
            notes = st.text_input("Notes")
        
        if st.form_submit_button("Add Account", use_container_width=True):
            if name and institution:
                db.add_account(
                    name=name,
                    institution=institution,
                    account_type=account_type,
                    current_balance=balance,
                    credit_limit=credit_limit if credit_limit > 0 else None,
                    minimum_payment=payment,
                    due_day=due_day,
                    is_business=is_business,
                    notes=notes
                )
                st.success(f"Added {name}")
                st.rerun()
            else:
                st.error("Name and Institution required")
