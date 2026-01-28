"""
Liquidity Engine - Dashboard (The Pulse)
Coming in Phase 4
"""
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import config
from utils import database as db
from utils.auth import require_auth

st.set_page_config(page_title="Dashboard | Liquidity Engine", page_icon="📊", layout="wide")

require_auth()

st.title("📊 Dashboard")
st.caption("The Pulse - Your Financial Command Center")

st.divider()

# Preview of what's coming
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 💵 True Cash Position")
    st.info("Coming in Phase 4")
    st.caption("Bank Balance minus upcoming credit card payments")

with col2:
    st.markdown("### 📈 Efficiency Ratio")
    st.info("Coming in Phase 4")
    st.caption("Revenue / Ad Spend (ROAS)")

with col3:
    st.markdown("### 🏠 Personal Draw")
    st.info("Coming in Phase 4")
    st.caption("Month-to-date lifestyle spending")

st.divider()

# Current debt summary (functional now)
st.markdown("### Current Debt Overview")

debt_by_type = db.get_debt_by_type()
if debt_by_type:
    cols = st.columns(len(debt_by_type))
    for i, row in enumerate(debt_by_type):
        with cols[i]:
            account_type = row['account_type'].replace('_', ' ').title()
            st.metric(account_type, f"${row['total']:,.2f}", f"{row['count']} accounts")

st.divider()
st.markdown("### 🚧 Phase 4 Features")
st.markdown("""
- **True Cash Position Widget** - Real available cash after obligations
- **Efficiency Ratio Tracker** - Monitor your ad spend ROAS
- **Personal Draw Meter** - Track lifestyle leakage
- **7-Day Payment Calendar** - Visual payment timeline
- **Account Health Grid** - Color-coded account status
""")
