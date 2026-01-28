"""
Run this script to update rewards points to current values.
Usage: python3 update_rewards.py
"""
import sqlite3
from pathlib import Path

db_path = Path(__file__).parent / "data" / "liquidity.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Delete old Alaska Airlines entry
cursor.execute("DELETE FROM rewards_points WHERE program_name = 'Alaska Airlines'")

# Update American Airlines
cursor.execute("""
    UPDATE rewards_points 
    SET current_balance = 26789, last_updated = '2026-01-27'
    WHERE program_name = 'American Airlines'
""")

# Add/update Atmos Rewards (Alaska + Hawaiian)
cursor.execute("""
    INSERT OR REPLACE INTO rewards_points (program_name, current_balance, point_value, last_updated)
    VALUES ('Atmos Rewards (Alaska/Hawaiian)', 551625, 0.014, '2026-01-27')
""")

conn.commit()
conn.close()

print("✅ Rewards updated!")
print("   - American Airlines: 26,789 miles")
print("   - Atmos Rewards (Alaska/Hawaiian): 551,625 points")
print("\nRefresh your browser to see the changes.")
