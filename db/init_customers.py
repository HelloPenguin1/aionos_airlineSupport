import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "customers.db"


def initialize_customers_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create Customers Table 
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            loyalty_tier TEXT NOT NULL,
            pnr TEXT UNIQUE NOT NULL,
            email TEXT,
            phone TEXT
        )
    """)

    # Customers travel history
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS travel_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            flights_last_12_months INTEGER NOT NULL,
            prior_complaints INTEGER NOT NULL,
            complaint_details TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    """)

    # Audit trail
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            pnr TEXT,
            user_message TEXT,
            intent TEXT,
            action TEXT,
            result TEXT,
            escalation_required INTEGER DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Ingest Data

    customers = [
        (
            "Priya Nair",
            "Gold",
            "SK4821X",
            "priya.nair@example.com",
            "+91-98xxxxxxx1"
        ),
        (
            "Arvind Kulkarni",
            "Silver",
            "TR1190B",
            "arvind.kulkarni@example.com",
            "+91-98xxxxxxx2"
        ),
        (
            "Meher Kaur",
            "Platinum",
            "WL7742",
            "meher.kaur@example.com",
            "+91-98xxxxxxx3"
        )
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO customers
        (name, loyalty_tier, pnr, email, phone)
        VALUES (?, ?, ?, ?, ?)
    """, customers)

    # --------------------------------------------------
    # Travel history
    # --------------------------------------------------

    travel_history = [
        (
            1,
            6,
            1,
            "Delayed baggage, resolved with voucher"
        ),
        (
            2,
            3,
            0,
            None
        ),
        (
            3,
            10,
            1,
            "Overbooking, resolved with a tier-status upgrade"
        )
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO travel_history
        (customer_id, flights_last_12_months, prior_complaints, complaint_details)
        VALUES (?, ?, ?, ?)
    """, travel_history)

    conn.commit()
    conn.close()

    print(f"Customer database initialized at: {DB_PATH}")


if __name__ == "__main__":
    initialize_customers_db()