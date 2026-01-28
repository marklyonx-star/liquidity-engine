"""
Update existing database with credit limits and rewards changes.
Run this after updating from an older version.
"""
import sqlite3
from pathlib import Path

db_path = Path(__file__).parent / "data" / "liquidity.db"

print("Updating database...")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Add credit_limit column if not exists
try:
    cursor.execute("ALTER TABLE accounts ADD COLUMN credit_limit DECIMAL(12,2)")
    print("Added credit_limit column")
except:
    print("credit_limit column already exists")

# Update credit limits for credit cards
credit_limits = {
    "Chase Ink Reserve": 150000,
    "Capital One Venture X": 30000,
    "Amex Gold (Ad Account)": 25000,
    "Amex Gold (Marketing)": 25000,
    "Amex Amazon": 10000,
    "Amex Plum": 50000,
    "Chase Sapphire": 15000,
    "Chase Biz Ink": 25000,
    "Capital One Savor": 10000,
    "John Lyon Card": 25000,
}

for name, limit in credit_limits.items():
    cursor.execute("UPDATE accounts SET credit_limit = ? WHERE name = ?", (limit, name))
    if cursor.rowcount > 0:
        print(f"  Updated {name}: ${limit:,}")

# Update rewards points
cursor.execute("DELETE FROM rewards_points WHERE program_name = 'Alaska Airlines'")
cursor.execute("""
    UPDATE rewards_points SET current_balance = 26789, last_updated = '2026-01-27'
    WHERE program_name = 'American Airlines'
""")
cursor.execute("""
    INSERT OR REPLACE INTO rewards_points (program_name, current_balance, point_value, last_updated)
    VALUES ('Atmos Rewards (Alaska/Hawaiian)', 551625, 0.014, '2026-01-27')
""")

conn.commit()
conn.close()

print("\n✅ Database updated successfully!")
print("\nCredit cards now have credit limits.")
print("Rewards updated: AA=26,789 | Atmos=551,625")
