"""
Liquidity Engine - Transactions
Coming in Phase 2-3
"""
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.auth import require_auth

st.set_page_config(page_title="Transactions | Liquidity Engine", page_icon="📥", layout="wide")

require_auth()

st.title("📥 Transactions")
st.caption("Import, view, and categorize your transactions")

st.divider()

st.info("🚧 **Coming in Phase 2-3**")

st.markdown("""
### Phase 2: CSV Import
- Upload Chase CSV exports
- Upload Capital One CSV exports  
- Upload Amex CSV exports
- Automatic duplicate detection
- Import history tracking

### Phase 3: Categorization
- Auto-categorization using smart rules
- Triage queue for uncategorized transactions
- Tag/project assignment (e.g., "NYC Trip")
- Learn from your categorization choices
""")

st.divider()

# Preview of the interface
st.markdown("### Preview: Transaction Import")

uploaded_file = st.file_uploader("Upload CSV from your bank", type=['csv'], disabled=True)

st.markdown("### Preview: Triage Queue")
st.caption("Uncategorized transactions will appear here for quick categorization")

# Mock triage interface
cols = st.columns([3, 1, 1, 1])
with cols[0]:
    st.text("AMAZON MARKETPLACE - $127.43")
with cols[1]:
    st.button("ENGINE", disabled=True, key="e1")
with cols[2]:
    st.button("OVERHEAD", disabled=True, key="o1")
with cols[3]:
    st.button("LIFESTYLE", disabled=True, key="l1")
