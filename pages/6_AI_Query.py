"""
Liquidity Engine - AI Query
Coming in Phase 5
"""
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.auth import require_auth

st.set_page_config(page_title="AI Query | Liquidity Engine", page_icon="🤖", layout="wide")

require_auth()

st.title("🤖 AI Query")
st.caption("Ask questions about your finances in plain English")

st.divider()

st.info("🚧 **Coming in Phase 5**")

# Preview interface
st.markdown("### Ask Claude about your finances")

query = st.text_input(
    "Your question",
    placeholder="e.g., What did my NYC trip cost me all in?",
    disabled=True
)

st.button("Ask", disabled=True, type="primary")

st.divider()

st.markdown("""
### Example Questions You'll Be Able to Ask:

**Spending Analysis**
- "What did my NYC trip cost me all in?"
- "How much did I spend on ads last month?"
- "Show me all restaurant expenses over $100"
- "What are my top 10 expenses this month?"

**Revenue & Performance**
- "What's my average weekly revenue?"
- "Compare Q4 vs Q3 revenue"
- "What's my ROAS for the last 30 days?"

**Cash Flow**
- "Project my cash position for next 30 days"
- "When will I run out of money if spending continues?"
- "What's my burn rate?"

**Debt Analysis**
- "How much do I owe on credit cards?"
- "When will the Sandra Lopez loan be paid off?"
- "What's my total monthly debt payment?"
""")

st.divider()

st.markdown("""
### How It Works (Phase 5):
1. You type a question in plain English
2. Claude interprets your question
3. The system queries your transaction database
4. Claude formats and explains the results
5. You can ask follow-up questions for clarification
""")
