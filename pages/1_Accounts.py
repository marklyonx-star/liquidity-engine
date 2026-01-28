"""
Liquidity Engine - Accounts Management
"""
import streamlit as st
import pandas as pd
from datetime import date, datetime
import sys
from pathlib import Path

# Add parent directory to path for imports
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

st.title("💳 Accounts")
st.caption("Manage your bank accounts, credit cards, and loans")

# Tabs for different views
tab1, tab2, tab3, tab4 = st.tabs(["📋 All Accounts", "➕ Add Account", "💎 Rewards Points", "📈 Balance History"])

# ============ TAB 1: All Accounts ============
with tab1:
    # Filter options
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        show_inactive = st.checkbox("Show inactive accounts", value=False)
    with col2:
        filter_type = st.selectbox("Filter by type", ["All"] + config.ACCOUNT_TYPES)
    with col3:
        sort_by = st.selectbox("Sort by", ["Balance (High to Low)", "Balance (Low to High)", "Due Date", "Name"])
    
    # Get accounts
    accounts = db.get_all_accounts(active_only=not show_inactive)
    
    if accounts:
        # Convert to dataframe for display
        accounts_data = []
        for acc in accounts:
            accounts_data.append({
                'id': acc['id'],
                'Account': acc['name'],
                'Institution': acc['institution'],
                'Type': acc['account_type'].replace('_', ' ').title(),
                'Balance': acc['current_balance'],
                'Payment Due': acc['minimum_payment'],
                'Due Day': acc['due_day'] if acc['due_day'] else '-',
                'Business': '✅' if acc['is_business'] else '❌',
                'Notes': acc['notes'] or ''
            })
        
        df = pd.DataFrame(accounts_data)
        
        # Apply filters
        if filter_type != "All":
            df = df[df['Type'] == filter_type.replace('_', ' ').title()]
        
        # Apply sorting
        if sort_by == "Balance (High to Low)":
            df = df.sort_values('Balance', ascending=False)
        elif sort_by == "Balance (Low to High)":
            df = df.sort_values('Balance', ascending=True)
        elif sort_by == "Due Date":
            df = df.sort_values('Due Day')
        elif sort_by == "Name":
            df = df.sort_values('Account')
        
        # Summary metrics
        st.divider()
        mcol1, mcol2, mcol3, mcol4 = st.columns(4)
        with mcol1:
            st.metric("Total Accounts", len(df))
        with mcol2:
            st.metric("Total Debt", f"${df['Balance'].sum():,.2f}")
        with mcol3:
            st.metric("Payments Due", f"${df['Payment Due'].sum():,.2f}")
        with mcol4:
            business_count = len(df[df['Business'] == '✅'])
            st.metric("Business / Personal", f"{business_count} / {len(df) - business_count}")
        
        st.divider()
        
        # Display accounts as expandable cards
        for idx, row in df.iterrows():
            with st.expander(f"**{row['Account']}** | ${row['Balance']:,.2f} | Due: {row['Due Day']}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Institution:** {row['Institution']}")
                    st.markdown(f"**Type:** {row['Type']}")
                    st.markdown(f"**Current Balance:** ${row['Balance']:,.2f}")
                    st.markdown(f"**Payment Due:** ${row['Payment Due']:,.2f}")
                    st.markdown(f"**Due Day:** {row['Due Day']}")
                    st.markdown(f"**Business Account:** {row['Business']}")
                    if row['Notes']:
                        st.markdown(f"**Notes:** {row['Notes']}")
                
                with col2:
                    st.markdown("##### Quick Update")
                    new_balance = st.number_input(
                        "New Balance",
                        value=float(row['Balance']),
                        step=100.0,
                        key=f"balance_{row['id']}"
                    )
                    
                    if st.button("Update Balance", key=f"update_{row['id']}"):
                        db.update_account_balance(row['id'], new_balance)
                        st.success("Balance updated!")
                        st.rerun()
                    
                    st.divider()
                    
                    if st.button("Edit Account", key=f"edit_{row['id']}"):
                        st.session_state['editing_account'] = row['id']
                        st.rerun()
    else:
        st.info("No accounts found. Add your first account in the 'Add Account' tab.")

# ============ TAB 2: Add/Edit Account ============
with tab2:
    st.markdown("### Add New Account")
    
    with st.form("add_account_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Account Name *", placeholder="e.g., Chase Ink Reserve")
            institution = st.text_input("Institution *", placeholder="e.g., Chase")
            account_type = st.selectbox("Account Type *", config.ACCOUNT_TYPES)
            last_four = st.text_input("Last 4 Digits", placeholder="e.g., 0678", max_chars=4)
            current_balance = st.number_input("Current Balance", value=0.0, step=100.0)
        
        with col2:
            credit_limit = st.number_input("Credit Limit (if applicable)", value=0.0, step=1000.0)
            minimum_payment = st.number_input("Monthly Payment", value=0.0, step=50.0)
            due_day = st.number_input("Due Day of Month", min_value=0, max_value=31, value=0, 
                                       help="Enter 0 if no specific due date")
            interest_rate = st.number_input("Interest Rate %", value=0.0, step=0.1)
            payoff_date = st.date_input("Payoff Date (if known)", value=None)
        
        is_business = st.checkbox("Business Account", value=True)
        notes = st.text_area("Notes", placeholder="Any additional notes about this account")
        
        submitted = st.form_submit_button("Add Account", type="primary")
        
        if submitted:
            if not name or not institution:
                st.error("Please fill in required fields (Account Name and Institution)")
            else:
                db.add_account(
                    name=name,
                    institution=institution,
                    account_type=account_type,
                    last_four=last_four if last_four else None,
                    current_balance=current_balance,
                    credit_limit=credit_limit if credit_limit > 0 else None,
                    minimum_payment=minimum_payment,
                    due_day=due_day if due_day > 0 else None,
                    interest_rate=interest_rate if interest_rate > 0 else None,
                    payoff_date=payoff_date.isoformat() if payoff_date else None,
                    is_business=is_business,
                    notes=notes if notes else None
                )
                st.success(f"Account '{name}' added successfully!")
                st.balloons()

# ============ TAB 3: Rewards Points ============
with tab3:
    st.markdown("### 💎 Rewards Points Tracker")
    
    rewards = db.get_all_rewards()
    total_value = db.get_total_rewards_value()
    
    # Summary
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("Total Estimated Value", f"${total_value:,.2f}")
    with col2:
        total_points = sum(r['current_balance'] for r in rewards)
        st.metric("Total Points", f"{total_points:,}")
    
    st.divider()
    
    # Rewards table with edit capability
    if rewards:
        for r in rewards:
            col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
            
            with col1:
                st.markdown(f"**{r['program_name']}**")
            with col2:
                st.markdown(f"{r['current_balance']:,} points")
            with col3:
                value = r['current_balance'] * (r['point_value'] or 0)
                st.markdown(f"≈ ${value:,.2f}")
            with col4:
                new_bal = st.number_input(
                    "Update",
                    value=r['current_balance'],
                    step=1000,
                    key=f"reward_{r['program_name']}",
                    label_visibility="collapsed"
                )
                if new_bal != r['current_balance']:
                    if st.button("Save", key=f"save_reward_{r['program_name']}"):
                        db.update_rewards_balance(r['program_name'], new_bal)
                        st.success("Updated!")
                        st.rerun()
    
    st.divider()
    
    # Add new rewards program
    st.markdown("##### Add New Rewards Program")
    with st.form("add_rewards"):
        col1, col2, col3 = st.columns(3)
        with col1:
            new_program = st.text_input("Program Name")
        with col2:
            new_points = st.number_input("Current Balance", value=0, step=1000)
        with col3:
            new_value = st.number_input("Value per Point", value=0.01, step=0.001, format="%.4f")
        
        if st.form_submit_button("Add Program"):
            if new_program:
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT OR IGNORE INTO rewards_points (program_name, current_balance, point_value, last_updated)
                        VALUES (?, ?, ?, ?)
                    """, (new_program, new_points, new_value, date.today().isoformat()))
                    conn.commit()
                st.success(f"Added {new_program}!")
                st.rerun()

# ============ TAB 4: Balance History ============
with tab4:
    st.markdown("### 📈 Balance History")
    st.info("Balance history is automatically recorded when you update account balances. As you use the app, trends will appear here.")
    
    # Select account to view history
    accounts = db.get_all_accounts()
    if accounts:
        account_names = {acc['id']: acc['name'] for acc in accounts}
        selected_account_id = st.selectbox(
            "Select Account",
            options=list(account_names.keys()),
            format_func=lambda x: account_names[x]
        )
        
        # Get balance history for selected account
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT balance_date, balance 
                FROM balance_history 
                WHERE account_id = ?
                ORDER BY balance_date DESC
                LIMIT 30
            """, (selected_account_id,))
            history = cursor.fetchall()
        
        if history:
            history_df = pd.DataFrame([dict(h) for h in history])
            history_df['balance_date'] = pd.to_datetime(history_df['balance_date'])
            
            # Simple line chart
            st.line_chart(history_df.set_index('balance_date')['balance'])
            
            # Data table
            st.dataframe(history_df, use_container_width=True)
        else:
            st.info("No balance history yet for this account. Update the balance to start tracking.")

# Sidebar summary
with st.sidebar:
    st.markdown("### Quick Actions")
    
    if st.button("🔄 Refresh Data"):
        st.rerun()
    
    st.divider()
    
    # Payment calendar preview
    st.markdown("### 📅 Upcoming Payments")
    upcoming = db.get_upcoming_payments()
    
    today = date.today().day
    for acc in upcoming:
        if acc['minimum_payment'] > 0 and acc['due_day']:
            days_until = acc['due_day'] - today
            if days_until < 0:
                days_until += 30  # Next month
            
            if days_until <= 7:
                color = "🔴" if days_until <= 3 else "🟡"
            else:
                color = "🟢"
            
            st.markdown(f"{color} **{acc['name'][:20]}**")
            st.caption(f"${acc['minimum_payment']:,.2f} | Day {acc['due_day']}")
