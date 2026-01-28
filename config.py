"""
Liquidity Engine - Configuration
"""
import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
IMPORTS_DIR = BASE_DIR / "imports"
RULES_DIR = BASE_DIR / "rules"

# Database
DATABASE_PATH = DATA_DIR / "liquidity.db"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
IMPORTS_DIR.mkdir(exist_ok=True)
RULES_DIR.mkdir(exist_ok=True)

# App Settings
APP_NAME = "Liquidity Engine"
APP_VERSION = "1.0.0"

# Dashboard Thresholds
CASH_WARNING_THRESHOLD = 50000  # Yellow zone below this
CASH_DANGER_THRESHOLD = 20000   # Red zone below this
CREDIT_UTILIZATION_WARNING = 0.50  # 50%
CREDIT_UTILIZATION_DANGER = 0.80   # 80%

# Forecast Settings
FORECAST_DAYS = 90

# Buckets
BUCKETS = ["ENGINE", "OVERHEAD", "LIFESTYLE"]

# Default Categories
DEFAULT_CATEGORIES = {
    "ENGINE": {
        "Revenue": ["Client Payments", "Consulting", "Other Income"],
        "Ad Spend": ["Facebook/Meta", "Google", "TikTok", "Other Platforms"],
        "Partner Payouts": ["Digital Viking", "Other Partners"],
        "Commissions": []
    },
    "OVERHEAD": {
        "Payroll": ["Gusto/Salaries", "Contractors"],
        "Debt Service": ["Credit Cards", "Personal Loans", "Auto Loan", "Tax Debt", "Private Loans"],
        "Subscriptions": ["Software", "Services"],
        "Insurance": [],
        "Professional Services": ["Legal", "Accounting"]
    },
    "LIFESTYLE": {
        "Dining": [],
        "Travel": ["Flights", "Hotels", "Transportation", "Activities"],
        "Entertainment": [],
        "Shopping": ["Mark", "Katie", "Gifts/Other"],
        "Home": [],
        "Health/Fitness": [],
        "Distributions/Draws": []
    }
}

# Account Types
ACCOUNT_TYPES = [
    "checking",
    "savings",
    "credit_card",
    "personal_loan",
    "auto_loan",
    "tax_debt",
    "private_loan",
    "other"
]
