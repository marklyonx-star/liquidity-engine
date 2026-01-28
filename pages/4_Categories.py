"""
Liquidity Engine - Categories
Coming in Phase 3
"""
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import config
from utils.auth import require_auth

st.set_page_config(page_title="Categories | Liquidity Engine", page_icon="🏷️", layout="wide")

require_auth()

st.title("🏷️ Categories")
st.caption("Manage your Three Buckets and categorization rules")

st.divider()

# Show the three buckets
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🚀 ENGINE")
    st.caption("Revenue & Cost of Goods Sold")
    for cat, subs in config.DEFAULT_CATEGORIES["ENGINE"].items():
        with st.expander(cat):
            if subs:
                for sub in subs:
                    st.markdown(f"- {sub}")
            else:
                st.caption("No subcategories")

with col2:
    st.markdown("### 🏢 OVERHEAD")
    st.caption("Fixed Costs & Debt Service")
    for cat, subs in config.DEFAULT_CATEGORIES["OVERHEAD"].items():
        with st.expander(cat):
            if subs:
                for sub in subs:
                    st.markdown(f"- {sub}")
            else:
                st.caption("No subcategories")

with col3:
    st.markdown("### 🏠 LIFESTYLE")
    st.caption("Personal & Distributions")
    for cat, subs in config.DEFAULT_CATEGORIES["LIFESTYLE"].items():
        with st.expander(cat):
            if subs:
                for sub in subs:
                    st.markdown(f"- {sub}")
            else:
                st.caption("No subcategories")

st.divider()

st.info("🚧 **Full category management coming in Phase 3**")

st.markdown("""
### Coming Features:
- Add/edit/delete categories and subcategories
- Create and manage tags (e.g., "NYC Trip", "Montana 2026")
- Auto-categorization rule builder
- Import/export category configurations
""")
