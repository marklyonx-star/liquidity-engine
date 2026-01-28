# 💰 Liquidity Engine

Personal & Business Finance Management System built for Mark Lyon.

## Quick Start

### 1. Install Dependencies

```bash
cd liquidity-engine
pip install -r requirements.txt
```

### 2. Run the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## What's Included (Phase 1)

✅ **16 Accounts Pre-loaded**
- All your credit cards (Chase, Amex, Capital One)
- Loans (Best Egg, LendingPoint, Land Rover)
- Private loans (Sandra Lopez, Martin Toha, John Lyon)
- Tax debt (IRS)

✅ **Rewards Points Tracking**
- Amex Membership Rewards
- Chase Ultimate Rewards
- Capital One Miles
- Airline miles

✅ **Account Management**
- View all accounts and balances
- Update balances with history tracking
- Add new accounts
- Payment due date tracking

✅ **Partner Draws Tracking (Mark & Katie)**
- Track personal draws from the business
- Side-by-side view of each partner's draws
- Import history from MK_Private.xlsx
- Running totals and difference tracking
- Add new draws manually
- Returns/credits supported (negative amounts)

## Navigation

| Page | Status | Description |
|------|--------|-------------|
| Home | ✅ Ready | Overview and quick stats |
| Accounts | ✅ Ready | Manage accounts, update balances |
| Dashboard | 🚧 Phase 4 | The "Pulse" - financial command center |
| Transactions | 🚧 Phase 2-3 | Import and categorize transactions |
| Categories | 🚧 Phase 3 | Manage the Three Buckets |
| Forecaster | 🚧 Phase 6 | 90-day cash flow projections |
| AI Query | 🚧 Phase 5 | Ask questions in plain English |
| Settings | ✅ Ready | Configure thresholds and rules |
| Partner Draws | ✅ Ready | Track draws between Mark & Katie |

## The Three Buckets

All transactions will be categorized into:

1. **ENGINE** - Revenue & Cost of Goods Sold (ad spend, partner payouts)
2. **OVERHEAD** - Fixed costs & Debt Service (payroll, loans, subscriptions)
3. **LIFESTYLE** - Personal spending & Distributions

## Your Current Debt Summary

| Account | Balance | Monthly Payment | Due Day |
|---------|---------|-----------------|---------|
| Chase Ink Reserve | $141,399 | $122,292 | 17th |
| Sandra Lopez | $117,000 | $3,000 | 1st |
| Land Rover | $63,941 | $1,596 | 27th |
| IRS Tax Debt | $40,378 | $1,230 | 15th |
| Best Egg | $32,545 | $1,284 | 7th |
| Martin Toha | $30,000 | TBD | - |
| John Lyon Card | $19,600 | $1,400 | 22nd |
| + Others | ... | ... | ... |

**Total Debt: $487,335**

## File Structure

```
liquidity-engine/
├── app.py              # Main entry point
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
├── data/
│   └── liquidity.db    # SQLite database (auto-created)
├── pages/
│   ├── 1_Accounts.py   # Account management
│   ├── 2_Dashboard.py  # Financial dashboard
│   ├── 3_Transactions.py
│   ├── 4_Categories.py
│   ├── 5_Forecaster.py
│   ├── 6_AI_Query.py
│   └── 7_Settings.py
└── utils/
    └── database.py     # Database operations
```

## Next Steps

Ready for **Phase 2**? We'll build:
- CSV import for Chase, Capital One, and Amex
- Duplicate detection
- Transaction parsing and normalization

Just say "Let's build Phase 2" when you're ready!

---

Built with ❤️ using Streamlit and SQLite
