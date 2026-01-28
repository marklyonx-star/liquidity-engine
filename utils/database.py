"""
Liquidity Engine - Database Operations
"""
import sqlite3
from datetime import datetime, date
from pathlib import Path
from contextlib import contextmanager
import config

@contextmanager
def get_connection():
    """Context manager for database connections."""
    conn = sqlite3.connect(config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_database():
    """Initialize the database with all tables."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Accounts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                institution TEXT NOT NULL,
                account_type TEXT NOT NULL,
                last_four TEXT,
                current_balance DECIMAL(12,2) DEFAULT 0,
                credit_limit DECIMAL(12,2),
                minimum_payment DECIMAL(12,2) DEFAULT 0,
                due_day INTEGER,
                interest_rate DECIMAL(5,2),
                payoff_date DATE,
                is_business BOOLEAN DEFAULT 1,
                is_active BOOLEAN DEFAULT 1,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                transaction_date DATE NOT NULL,
                post_date DATE,
                description TEXT NOT NULL,
                clean_description TEXT,
                amount DECIMAL(12,2) NOT NULL,
                transaction_type TEXT,
                bucket TEXT,
                category TEXT,
                subcategory TEXT,
                tag TEXT,
                is_categorized BOOLEAN DEFAULT 0,
                is_reviewed BOOLEAN DEFAULT 0,
                auto_categorized BOOLEAN DEFAULT 0,
                merchant_name TEXT,
                reference_number TEXT,
                notes TEXT,
                import_hash TEXT UNIQUE,
                imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES accounts(id)
            )
        """)
        
        # Categories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bucket TEXT NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT,
                is_active BOOLEAN DEFAULT 1,
                display_order INTEGER,
                UNIQUE(bucket, category, subcategory)
            )
        """)
        
        # Tags table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                start_date DATE,
                end_date DATE,
                budget DECIMAL(12,2),
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Auto-categorization rules table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auto_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_pattern TEXT NOT NULL,
                match_type TEXT DEFAULT 'contains',
                bucket TEXT NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT,
                tag TEXT,
                priority INTEGER DEFAULT 100,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Recurring transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recurring_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER,
                description TEXT NOT NULL,
                expected_amount DECIMAL(12,2),
                frequency TEXT NOT NULL,
                day_of_month INTEGER,
                day_of_week INTEGER,
                bucket TEXT,
                category TEXT,
                subcategory TEXT,
                is_income BOOLEAN DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                last_occurrence DATE,
                next_expected DATE,
                notes TEXT,
                FOREIGN KEY (account_id) REFERENCES accounts(id)
            )
        """)
        
        # Balance history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS balance_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                balance_date DATE NOT NULL,
                balance DECIMAL(12,2) NOT NULL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES accounts(id),
                UNIQUE(account_id, balance_date)
            )
        """)
        
        # Rewards points table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rewards_points (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                program_name TEXT NOT NULL UNIQUE,
                current_balance INTEGER DEFAULT 0,
                point_value DECIMAL(6,4),
                last_updated DATE,
                notes TEXT
            )
        """)
        
        # Partner draws table (Mark & Kelly personal draws from business)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS partner_draws (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                partner TEXT NOT NULL,
                draw_date DATE NOT NULL,
                description TEXT NOT NULL,
                amount DECIMAL(12,2) NOT NULL,
                notes TEXT,
                transaction_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (transaction_id) REFERENCES transactions(id)
            )
        """)
        
        conn.commit()

def seed_initial_data():
    """Seed the database with Mark's accounts and initial data."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Check if accounts already exist
        cursor.execute("SELECT COUNT(*) FROM accounts")
        if cursor.fetchone()[0] > 0:
            return  # Already seeded
        
        # Insert accounts
        accounts = [
            # Credit Cards
            ("Chase Ink Reserve", "Chase", "credit_card", "0678", 141398.50, None, 122291.79, 17, None, None, 1, 1, "CRITICAL: Huge payment due"),
            ("Capital One Venture X", "Capital One", "credit_card", "8615", 17538.56, None, 17538.56, 20, None, None, 1, 1, "Pay Full Balance"),
            ("Amex Gold (Ad Account)", "Amex", "credit_card", "51008", 6560.22, None, 4355.21, 2, None, None, 1, 1, "Primary ad spend card"),
            ("Amex Gold (Marketing)", "Amex", "credit_card", "51001", 5465.09, None, 1282.11, 18, None, None, 1, 1, "Marketing Card"),
            ("Amex Amazon", "Amex", "credit_card", "61002", 1111.63, None, 35.00, 15, None, None, 1, 1, "Amazon Prime"),
            ("Amex Plum", "Amex", "credit_card", "31003", 235.60, None, 0, None, None, None, 1, 1, "Flexible Pay"),
            ("Chase Sapphire", "Chase", "credit_card", "5125", 887.07, None, 0, 4, None, None, 0, 1, "Personal"),
            ("Chase Biz Ink", "Chase", "credit_card", "8187", 0, None, 0, 9, None, None, 1, 1, "Zero Balance"),
            ("Capital One Savor", "Capital One", "credit_card", "5920", 1929.86, None, 1929.86, None, None, None, 0, 1, "Personal card"),
            
            # Loans
            ("Tax Debt (Katie)", "IRS", "tax_debt", None, 40377.78, None, 1230.00, 15, None, None, 1, 1, "2020/2021 Taxes"),
            ("Land Rover Auto Loan", "Land Rover Financial", "auto_loan", None, 63940.87, None, 1596.07, 27, None, "2029-07-27", 0, 1, "Loan Ends July 2029"),
            ("Best Egg Personal Loan", "Best Egg", "personal_loan", "1753", 32545.15, None, 1283.58, 7, None, None, 0, 1, "Autopay ON"),
            ("LendingPoint Personal Loan", "LendingPoint", "personal_loan", "6143", 8744.74, None, 1139.15, 23, None, None, 0, 1, "16 Payments Left"),
            
            # Private Loans
            ("Sandra Lopez Loan", "Sandra Lopez", "private_loan", None, 117000.00, None, 3000.00, 1, 0, None, 0, 1, "No interest - straight paydown"),
            ("John Lyon Card", "Chase (for John Lyon)", "credit_card", None, 19600.00, None, 1400.00, 22, None, "2027-03-21", 0, 1, "Paying on behalf of John Lyon"),
            ("Martin Toha", "Martin Toha", "private_loan", None, 30000.00, None, 0, None, None, None, 0, 1, "No payment plan yet - track balance only"),
        ]
        
        cursor.executemany("""
            INSERT INTO accounts (name, institution, account_type, last_four, current_balance, 
                                  credit_limit, minimum_payment, due_day, interest_rate, payoff_date,
                                  is_business, is_active, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, accounts)
        
        # Insert rewards points
        rewards = [
            ("Amex Membership Rewards", 1148376, 0.015, "2026-01-27"),
            ("Chase Ultimate Rewards", 985997, 0.015, "2026-01-27"),
            ("Capital One Miles", 313946, 0.01, "2026-01-27"),
            ("Amazon Rewards", 221369, 0.01, "2026-01-27"),
            ("American Airlines", 26789, 0.014, "2026-01-27"),
            ("Atmos Rewards (Alaska/Hawaiian)", 551625, 0.014, "2026-01-27"),
        ]
        
        cursor.executemany("""
            INSERT INTO rewards_points (program_name, current_balance, point_value, last_updated)
            VALUES (?, ?, ?, ?)
        """, rewards)
        
        # Insert default categories
        order = 0
        for bucket, categories in config.DEFAULT_CATEGORIES.items():
            for category, subcategories in categories.items():
                if subcategories:
                    for subcategory in subcategories:
                        cursor.execute("""
                            INSERT OR IGNORE INTO categories (bucket, category, subcategory, display_order)
                            VALUES (?, ?, ?, ?)
                        """, (bucket, category, subcategory, order))
                        order += 1
                else:
                    cursor.execute("""
                        INSERT OR IGNORE INTO categories (bucket, category, subcategory, display_order)
                        VALUES (?, ?, NULL, ?)
                    """, (bucket, category, order))
                    order += 1
        
        # Insert default auto-categorization rules
        rules = [
            ("NEWLIN", "contains", "ENGINE", "Revenue", "Client Payments", None, 10),
            ("RME", "contains", "ENGINE", "Revenue", "Client Payments", None, 10),
            ("FACEBOOK", "contains", "ENGINE", "Ad Spend", "Facebook/Meta", None, 20),
            ("META ADS", "contains", "ENGINE", "Ad Spend", "Facebook/Meta", None, 20),
            ("GOOGLE ADS", "contains", "ENGINE", "Ad Spend", "Google", None, 20),
            ("TIKTOK", "contains", "ENGINE", "Ad Spend", "TikTok", None, 20),
            ("DIGITAL VIKING", "contains", "ENGINE", "Partner Payouts", "Digital Viking", None, 30),
            ("GUSTO", "contains", "OVERHEAD", "Payroll", "Gusto/Salaries", None, 40),
            ("BEST EGG", "contains", "OVERHEAD", "Debt Service", "Personal Loans", None, 50),
            ("LENDINGPOINT", "contains", "OVERHEAD", "Debt Service", "Personal Loans", None, 50),
            ("LAND ROVER FIN", "contains", "OVERHEAD", "Debt Service", "Auto Loan", None, 50),
            ("IRS", "contains", "OVERHEAD", "Debt Service", "Tax Debt", None, 50),
            ("EFTPS", "contains", "OVERHEAD", "Debt Service", "Tax Debt", None, 50),
        ]
        
        cursor.executemany("""
            INSERT INTO auto_rules (match_pattern, match_type, bucket, category, subcategory, tag, priority)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, rules)
        
        conn.commit()

# ============ Account Operations ============

def get_all_accounts(active_only=True):
    """Get all accounts."""
    with get_connection() as conn:
        cursor = conn.cursor()
        if active_only:
            cursor.execute("SELECT * FROM accounts WHERE is_active = 1 ORDER BY current_balance DESC")
        else:
            cursor.execute("SELECT * FROM accounts ORDER BY current_balance DESC")
        return cursor.fetchall()

def get_account_by_id(account_id):
    """Get a single account by ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM accounts WHERE id = ?", (account_id,))
        return cursor.fetchone()

def add_account(name, institution, account_type, last_four=None, current_balance=0,
                credit_limit=None, minimum_payment=0, due_day=None, interest_rate=None,
                payoff_date=None, is_business=True, notes=None):
    """Add a new account."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO accounts (name, institution, account_type, last_four, current_balance,
                                  credit_limit, minimum_payment, due_day, interest_rate,
                                  payoff_date, is_business, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, institution, account_type, last_four, current_balance,
              credit_limit, minimum_payment, due_day, interest_rate,
              payoff_date, is_business, notes))
        conn.commit()
        return cursor.lastrowid

def update_account(account_id, **kwargs):
    """Update an account's fields."""
    if not kwargs:
        return
    
    # Build the SET clause dynamically
    set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
    values = list(kwargs.values()) + [account_id]
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            UPDATE accounts 
            SET {set_clause}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, values)
        conn.commit()

def update_account_balance(account_id, new_balance):
    """Update an account's balance and record in history."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Update current balance
        cursor.execute("""
            UPDATE accounts 
            SET current_balance = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (new_balance, account_id))
        
        # Record in balance history
        today = date.today().isoformat()
        cursor.execute("""
            INSERT OR REPLACE INTO balance_history (account_id, balance_date, balance)
            VALUES (?, ?, ?)
        """, (account_id, today, new_balance))
        
        conn.commit()

def delete_account(account_id):
    """Soft delete an account (set inactive)."""
    update_account(account_id, is_active=False)

# ============ Summary Functions ============

def get_total_debt():
    """Get total debt across all accounts."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COALESCE(SUM(current_balance), 0) as total
            FROM accounts 
            WHERE is_active = 1 AND current_balance > 0
        """)
        return cursor.fetchone()['total']

def get_monthly_obligations():
    """Get total monthly payment obligations."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COALESCE(SUM(minimum_payment), 0) as total
            FROM accounts 
            WHERE is_active = 1 AND minimum_payment > 0
        """)
        return cursor.fetchone()['total']

def get_upcoming_payments(days=7):
    """Get payments due in the next N days."""
    with get_connection() as conn:
        cursor = conn.cursor()
        today = date.today().day
        
        # Calculate which due days fall within the window
        # This is simplified - in production you'd handle month boundaries
        cursor.execute("""
            SELECT * FROM accounts 
            WHERE is_active = 1 
            AND minimum_payment > 0 
            AND due_day IS NOT NULL
            ORDER BY due_day
        """)
        return cursor.fetchall()

def get_debt_by_type():
    """Get debt totals grouped by account type."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT account_type, SUM(current_balance) as total, COUNT(*) as count
            FROM accounts 
            WHERE is_active = 1 AND current_balance > 0
            GROUP BY account_type
            ORDER BY total DESC
        """)
        return cursor.fetchall()

# ============ Rewards Points ============

def get_all_rewards():
    """Get all rewards programs."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM rewards_points ORDER BY current_balance DESC")
        return cursor.fetchall()

def update_rewards_balance(program_name, new_balance):
    """Update a rewards program balance."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE rewards_points 
            SET current_balance = ?, last_updated = ?
            WHERE program_name = ?
        """, (new_balance, date.today().isoformat(), program_name))
        conn.commit()

def get_total_rewards_value():
    """Get total estimated value of all rewards points."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COALESCE(SUM(current_balance * point_value), 0) as total
            FROM rewards_points
        """)
        return cursor.fetchone()['total']

# Initialize database on import
init_database()
seed_initial_data()

# ============ Partner Draws ============

def add_partner_draw(partner, draw_date, description, amount, notes=None, transaction_id=None):
    """Add a new partner draw entry."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO partner_draws (partner, draw_date, description, amount, notes, transaction_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (partner, draw_date, description, amount, notes, transaction_id))
        conn.commit()
        return cursor.lastrowid

def get_partner_draws(partner=None, start_date=None, end_date=None):
    """Get partner draws with optional filters."""
    with get_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM partner_draws WHERE 1=1"
        params = []
        
        if partner:
            query += " AND partner = ?"
            params.append(partner)
        if start_date:
            query += " AND draw_date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND draw_date <= ?"
            params.append(end_date)
        
        query += " ORDER BY draw_date DESC, id DESC"
        cursor.execute(query, params)
        return cursor.fetchall()

def get_partner_totals():
    """Get total draws for each partner."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT partner, 
                   COALESCE(SUM(amount), 0) as total,
                   COUNT(*) as count
            FROM partner_draws
            GROUP BY partner
        """)
        results = cursor.fetchall()
        totals = {'Mark': 0, 'Katie': 0, 'Mark_count': 0, 'Katie_count': 0}
        for row in results:
            totals[row['partner']] = row['total']
            totals[f"{row['partner']}_count"] = row['count']
        return totals

def delete_partner_draw(draw_id):
    """Delete a partner draw entry."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM partner_draws WHERE id = ?", (draw_id,))
        conn.commit()

def update_partner_draw(draw_id, **kwargs):
    """Update a partner draw entry."""
    if not kwargs:
        return
    set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
    values = list(kwargs.values()) + [draw_id]
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE partner_draws SET {set_clause} WHERE id = ?", values)
        conn.commit()

def import_partner_draws_from_excel(filepath):
    """Import partner draws from the MK_Private.xlsx format."""
    import pandas as pd
    from datetime import datetime
    
    df = pd.read_excel(filepath, sheet_name='Draw 2025', header=None)
    
    imported = {'Mark': 0, 'Katie': 0}
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Clear existing draws (optional - could also append)
        cursor.execute("DELETE FROM partner_draws")
        
        # Import Katie's entries (columns 0-3)
        # Track the last valid date for entries without dates
        last_katie_date = None
        for idx, row in df.iloc[1:].iterrows():  # Skip header row
            draw_date = row[0]
            description = row[1]
            amount = row[2]
            notes = row[3] if pd.notna(row[3]) else None
            
            # Skip if no description or amount
            if pd.isna(description) or pd.isna(amount):
                continue
            
            # Handle missing date - use last valid date or a placeholder
            if pd.notna(draw_date):
                if isinstance(draw_date, datetime):
                    draw_date = draw_date.strftime('%Y-%m-%d')
                else:
                    draw_date = str(draw_date)
                last_katie_date = draw_date
            else:
                # Use last valid date if available, otherwise use placeholder
                draw_date = last_katie_date if last_katie_date else '2024-01-01'
            
            cursor.execute("""
                INSERT INTO partner_draws (partner, draw_date, description, amount, notes)
                VALUES (?, ?, ?, ?, ?)
            """, ('Katie', draw_date, str(description), float(amount), notes))
            imported['Katie'] += 1
        
        # Import Mark's entries (columns 5-7)
        # Mark's entries often don't have their own date - use Katie's date from same row
        last_mark_date = None
        for idx, row in df.iloc[1:].iterrows():
            mark_date = row[5]  # Mark's date column (often empty)
            description = row[6]
            amount = row[7]
            katie_date = row[0]  # Katie's date on same row
            
            # Skip if no description or amount
            if pd.isna(description) or pd.isna(amount):
                continue
            
            # Determine the date to use (priority: Mark's date > Katie's date > last date > fallback)
            if pd.notna(mark_date):
                if isinstance(mark_date, datetime):
                    draw_date = mark_date.strftime('%Y-%m-%d')
                else:
                    draw_date = str(mark_date)
            elif pd.notna(katie_date):
                if isinstance(katie_date, datetime):
                    draw_date = katie_date.strftime('%Y-%m-%d')
                else:
                    draw_date = str(katie_date)
            elif last_mark_date:
                draw_date = last_mark_date
            else:
                draw_date = '2024-01-01'
            
            last_mark_date = draw_date
            
            cursor.execute("""
                INSERT INTO partner_draws (partner, draw_date, description, amount, notes)
                VALUES (?, ?, ?, ?, ?)
            """, ('Mark', str(draw_date), str(description), float(amount), None))
            imported['Mark'] += 1
        
        conn.commit()
    
    return imported
