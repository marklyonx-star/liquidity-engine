"""
Liquidity Engine - Settings
"""
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import config
from utils import database as db
from utils.auth import require_auth

st.set_page_config(page_title="Settings | Liquidity Engine", page_icon="⚙️", layout="wide")

require_auth()

st.title("⚙️ Settings")
st.caption("Configure your Liquidity Engine")

st.divider()

tab1, tab2, tab3 = st.tabs(["🎯 Thresholds", "🤖 Auto-Rules", "💾 Data"])

with tab1:
    st.markdown("### Dashboard Thresholds")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Cash Position Alerts")
        warning = st.number_input(
            "Warning Threshold (Yellow Zone)",
            value=config.CASH_WARNING_THRESHOLD,
            step=5000,
            help="You'll see yellow when cash drops below this"
        )
        danger = st.number_input(
            "Danger Threshold (Red Zone)",
            value=config.CASH_DANGER_THRESHOLD,
            step=5000,
            help="You'll see red when cash drops below this"
        )
    
    with col2:
        st.markdown("#### Credit Utilization Alerts")
        util_warning = st.slider(
            "Warning Level",
            min_value=0.0,
            max_value=1.0,
            value=config.CREDIT_UTILIZATION_WARNING,
            format="%.0f%%",
            help="Yellow alert when utilization exceeds this"
        )
        util_danger = st.slider(
            "Danger Level",
            min_value=0.0,
            max_value=1.0,
            value=config.CREDIT_UTILIZATION_DANGER,
            format="%.0f%%",
            help="Red alert when utilization exceeds this"
        )
    
    st.info("Threshold changes will be saved to your configuration in a future update.")

with tab2:
    st.markdown("### Auto-Categorization Rules")
    st.caption("Rules that automatically categorize transactions based on description matching")
    
    # Show current rules
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM auto_rules WHERE is_active = 1 ORDER BY priority")
        rules = cursor.fetchall()
    
    if rules:
        for rule in rules:
            col1, col2, col3, col4 = st.columns([2, 1, 2, 1])
            with col1:
                st.markdown(f"**{rule['match_pattern']}**")
            with col2:
                st.caption(rule['match_type'])
            with col3:
                st.markdown(f"{rule['bucket']} → {rule['category']}")
            with col4:
                st.caption(f"Priority: {rule['priority']}")
    
    st.divider()
    
    st.markdown("##### Add New Rule")
    with st.form("add_rule"):
        col1, col2 = st.columns(2)
        with col1:
            pattern = st.text_input("Match Pattern", placeholder="e.g., STARBUCKS")
            match_type = st.selectbox("Match Type", ["contains", "exact", "regex"])
        with col2:
            bucket = st.selectbox("Bucket", config.BUCKETS)
            category = st.text_input("Category", placeholder="e.g., Dining")
        
        if st.form_submit_button("Add Rule"):
            if pattern and category:
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO auto_rules (match_pattern, match_type, bucket, category, priority)
                        VALUES (?, ?, ?, ?, 100)
                    """, (pattern.upper(), match_type, bucket, category))
                    conn.commit()
                st.success("Rule added!")
                st.rerun()

with tab3:
    st.markdown("### Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Database Info")
        st.markdown(f"**Location:** `{config.DATABASE_PATH}`")
        
        # Get database stats
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM accounts")
            acc_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM transactions")
            txn_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM auto_rules")
            rule_count = cursor.fetchone()[0]
        
        st.markdown(f"**Accounts:** {acc_count}")
        st.markdown(f"**Transactions:** {txn_count}")
        st.markdown(f"**Auto-Rules:** {rule_count}")
    
    with col2:
        st.markdown("#### Danger Zone")
        st.warning("These actions cannot be undone!")
        
        if st.button("🗑️ Clear All Transactions", type="secondary"):
            st.session_state['confirm_clear_txn'] = True
        
        if st.session_state.get('confirm_clear_txn'):
            if st.button("⚠️ Yes, delete all transactions", type="primary"):
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM transactions")
                    conn.commit()
                st.success("All transactions deleted.")
                st.session_state['confirm_clear_txn'] = False
                st.rerun()

# Version info
st.divider()
st.caption(f"Liquidity Engine v{config.APP_VERSION}")
