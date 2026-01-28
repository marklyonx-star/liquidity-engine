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

# Custom CSS for mobile-friendly display
st.markdown("""
<style>
    /* Compact display */
    [data-testid="stMetricValue"] { font-size: 1.1rem !important; }
    [data-testid="stMetricLabel"] { font-size: 0.75rem !important; }
    .block-container { padding: 1rem !important; }
    h1 { font-size: 1.4rem !important; }
    h2 { font-size: 1.2rem !important; }
    h3 { font-size: 1rem !important; }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #0e1117;
    }
    [data-testid="stSidebar"] [data-testid="stMetricValue"] { 
        font-size: 1rem !important; 
    }
</style>
""", unsafe_allow_html=True)

# Sidebar - compact
with st.sidebar:
    st.markdown("### 💰 Liquidity Engine")
    st.caption(f"v{config.APP_VERSION}")
    
    st.divider()
    
    total_debt = db.get_total_debt()
    monthly_obligations = db.get_monthly_obligations()
    rewards_value = db.get_total_rewards_value()
    
    st.metric("Debt", f"${total_debt/1000:.0f}K")
    st.metric("Due", f"${monthly_obligations/1000:.0f}K")
    st.metric("Rewards", f"${rewards_value/1000:.0f}K")

# Main content - compact
st.markdown("## 💰 Liquidity Engine")

# Quick metrics row
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Debt", f"${total_debt/1000:.0f}K")
with col2:
    st.metric("Payments Due", f"${monthly_obligations/1000:.0f}K")
with col3:
    st.metric("Rewards", f"${rewards_value/1000:.0f}K")

st.divider()

# Debt breakdown - collapsible
with st.expander("📊 Debt Breakdown", expanded=True):
    debt_by_type = db.get_debt_by_type()
    for row in debt_by_type:
        account_type = row['account_type'].replace('_', ' ').title()
        st.markdown(f"**{account_type}:** ${row['total']:,.0f} ({row['count']} accounts)")

# Upcoming payments - collapsible
with st.expander("📅 Upcoming Payments", expanded=False):
    upcoming = db.get_upcoming_payments(days=30)
    if upcoming:
        for payment in upcoming[:8]:
            if payment['minimum_payment'] > 0:
                st.markdown(f"• **{payment['name'][:20]}**: ${payment['minimum_payment']:,.0f} (Day {payment['due_day']})")
    else:
        st.caption("No upcoming payments")

# Rewards - collapsible
with st.expander("✨ Rewards Points", expanded=False):
    rewards = db.get_all_rewards()
    for r in rewards:
        value = r['current_balance'] * r['point_value']
        st.markdown(f"**{r['program_name'][:20]}**: {r['current_balance']:,} pts (${value:,.0f})")

st.divider()

# Quick navigation
st.markdown("### Quick Navigation")
c1, c2 = st.columns(2)
with c1:
    if st.button("📊 Dashboard", use_container_width=True):
        st.switch_page("pages/2_Dashboard.py")
    if st.button("💳 Accounts", use_container_width=True):
        st.switch_page("pages/1_Accounts.py")
with c2:
    if st.button("👫 Partner Draws", use_container_width=True):
        st.switch_page("pages/8_Partner_Draws.py")
    if st.button("⚙️ Settings", use_container_width=True):
        st.switch_page("pages/7_Settings.py")

st.divider()
st.caption(f"v{config.APP_VERSION} | Data stored locally")
