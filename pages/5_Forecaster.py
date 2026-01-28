"""
Liquidity Engine - Forecaster (Crystal Ball)
Coming in Phase 6
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date, timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import database as db
from utils.auth import require_auth

st.set_page_config(page_title="Forecaster | Liquidity Engine", page_icon="🔮", layout="wide")

require_auth()

st.title("🔮 Forecaster")
st.caption("The Crystal Ball - Predict and prevent cash crunches")

st.divider()

st.info("🚧 **Coming in Phase 6**")

# Show a preview with current data
st.markdown("### Preview: 90-Day Cash Flow Projection")

# Mock data for preview
start_balance = 200000  # Placeholder

# Generate mock forecast
dates = [date.today() + timedelta(days=i) for i in range(90)]
balances = [start_balance]

# Get actual monthly obligations
monthly_payments = db.get_monthly_obligations()

for i in range(1, 90):
    # Simulate daily changes
    daily_change = -monthly_payments / 30  # Spread monthly payments
    if dates[i].day == 15:  # Simulate revenue on 15th
        daily_change += 100000
    balances.append(balances[-1] + daily_change)

# Create visualization
fig = go.Figure()

# Add balance line
fig.add_trace(go.Scatter(
    x=dates,
    y=balances,
    mode='lines',
    name='Projected Balance',
    line=dict(color='#00cc00', width=2)
))

# Add danger zone
fig.add_hline(y=20000, line_dash="dash", line_color="red", 
              annotation_text="Danger Zone ($20k)")
fig.add_hline(y=50000, line_dash="dash", line_color="orange",
              annotation_text="Warning Zone ($50k)")

fig.update_layout(
    title="Projected Cash Balance (Mock Data)",
    xaxis_title="Date",
    yaxis_title="Balance ($)",
    hovermode="x unified",
    template="plotly_dark"
)

st.plotly_chart(fig, use_container_width=True)

st.caption("⚠️ This is a preview with simulated data. Actual forecasting will use your real transactions and recurring payments.")

st.divider()

st.markdown("""
### Phase 6 Features:
- **Recurring Transaction Setup** - Define expected income and expenses
- **Cash Flow Projection Engine** - 90-day forward projection
- **Waterline Visualization** - Green/Yellow/Red zones
- **Liquidity Alerts** - Get warned before cash crunches
- **What-If Scenarios** - Test different spending/income scenarios
""")

# Show current payment schedule
st.divider()
st.markdown("### Current Payment Schedule")

accounts = db.get_all_accounts()
payments = [(a['name'], a['minimum_payment'], a['due_day']) 
            for a in accounts if a['minimum_payment'] and a['minimum_payment'] > 0]
payments.sort(key=lambda x: x[2] if x[2] else 32)

if payments:
    df = pd.DataFrame(payments, columns=['Account', 'Payment', 'Due Day'])
    df['Payment'] = df['Payment'].apply(lambda x: f"${x:,.2f}")
    st.dataframe(df, use_container_width=True, hide_index=True)
