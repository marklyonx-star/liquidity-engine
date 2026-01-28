"""
Liquidity Engine - Main Application
Personal & Business Finance Management System
"""
import streamlit as st
import config
from utils import database as db

# Page configuration
st.set_page_config(
    page_title=config.APP_NAME,
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ PASSWORD PROTECTION ============
def check_password():
    """Returns True if the user has entered the correct password."""
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets.get("password", "lyon2026"):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False

    # First run or password not correct
    if "password_correct" not in st.session_state:
        st.markdown("## 🔐 Liquidity Engine")
        st.text_input(
            "Enter password", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        st.caption("Contact Mark for access")
        return False
    
    # Password correct
    if st.session_state["password_correct"]:
        return True
    
    # Password incorrect
    st.markdown("## 🔐 Liquidity Engine")
    st.text_input(
        "Enter password", 
        type="password", 
        on_change=password_entered, 
        key="password"
    )
    st.error("😕 Incorrect password")
    return False

if not check_password():
    st.stop()

# ============ MAIN APP (only shows after password) ============

# Custom CSS
st.markdown("""
<style>
    /* Main metrics styling */
    [data-testid="metric-container"] {
        background-color: #1e1e1e;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #333;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #0e1117;
    }
    
    /* Table styling */
    .dataframe {
        font-size: 14px;
    }
    
    /* Debt amount styling */
    .debt-critical {
        color: #ff4b4b;
        font-weight: bold;
    }
    
    .debt-warning {
        color: #ffa500;
    }
    
    .debt-ok {
        color: #00cc00;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("💰 Liquidity Engine")
    st.caption(f"v{config.APP_VERSION}")
    
    st.divider()
    
    # Quick Stats
    total_debt = db.get_total_debt()
    monthly_obligations = db.get_monthly_obligations()
    rewards_value = db.get_total_rewards_value()
    
    st.metric("Total Debt", f"${total_debt:,.2f}")
    st.metric("Payments Due", f"${monthly_obligations:,.2f}")
    st.metric("Rewards Value", f"${rewards_value:,.2f}")
    
    st.divider()
    
    st.caption("Navigate using the pages above ☝️")

# Main content
st.title("Welcome to Liquidity Engine")
st.markdown("### Your Personal & Business Finance Command Center")

st.divider()

# Quick overview cards
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 🔴 Total Debt")
    st.markdown(f"## ${total_debt:,.2f}")
    
    # Debt breakdown
    debt_by_type = db.get_debt_by_type()
    for row in debt_by_type:
        account_type = row['account_type'].replace('_', ' ').title()
        st.caption(f"{account_type}: ${row['total']:,.2f} ({row['count']} accounts)")

with col2:
    st.markdown("#### 📅 Payments Due")
    st.markdown(f"## ${monthly_obligations:,.2f}")
    
    # Upcoming payments
    upcoming = db.get_upcoming_payments(days=7)
    if upcoming:
        st.caption("Due this month:")
        for payment in upcoming[:5]:
            if payment['minimum_payment'] > 0:
                st.caption(f"• {payment['name']}: ${payment['minimum_payment']:,.2f} (Day {payment['due_day']})")

with col3:
    st.markdown("#### ✨ Rewards Assets")
    st.markdown(f"## ${rewards_value:,.2f}")
    
    rewards = db.get_all_rewards()
    for r in rewards[:4]:
        st.caption(f"{r['program_name']}: {r['current_balance']:,} pts")

st.divider()

# Getting Started Guide
st.markdown("### 🚀 Getting Started")

st.markdown("""
**Phase 1 is complete!** Your accounts are loaded and ready. Here's what you can do:

1. **📊 Dashboard** - View your financial pulse (coming in Phase 4)
2. **💳 Accounts** - Manage and update your account balances  
3. **📥 Transactions** - Import and categorize transactions (coming in Phase 2)
4. **🏷️ Categories** - Customize your three buckets (coming in Phase 3)
5. **🔮 Forecaster** - Predict cash crunches (coming in Phase 6)
6. **🤖 AI Query** - Ask questions in plain English (coming in Phase 5)

**Next step:** Go to the **Accounts** page to review your loaded accounts and update any balances.
""")

# Version info
st.divider()
st.caption(f"Liquidity Engine v{config.APP_VERSION} | Built for Mark Lyon | Data stored locally in SQLite")
