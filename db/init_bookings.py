import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "bookings.db"


def initialize_bookings_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            pnr TEXT NOT NULL,
            flight TEXT NOT NULL,
            route TEXT NOT NULL,
            travel_date TEXT NOT NULL,
            original_departure TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)

    bookings = [
        (
            "Priya Nair",
            "SK4821X",
            "SK-204",
            "Delhi → Goa",
            "2026-09-23",
            "18:40",
            "Cancelled due to operational reasons"
        ),
        (
            "Priya Nair",
            "SK4821X",
            "Return",
            "Goa → Delhi",
            "2026-09-25",
            "16:20",
            "Unaffected"
        ),
        (
            "Arvind Kulkarni",
            "TR1190B",
            "SK-118",
            "Mumbai → Bengaluru",
            "2026-09-23",
            "07:10",
            "Delayed 4h, new departure 11:10"
        ),
        (
            "Meher Kaur",
            "WL7742",
            "SK-305",
            "Delhi → Hyderabad",
            "2026-09-23",
            "14:00",
            "Delayed 6h, new departure 20:00"
        )
    ]

    cursor.executemany("""
        INSERT INTO bookings
        (customer_name, pnr, flight, route, travel_date,
         original_departure, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, bookings)

    conn.commit()
    conn.close()

    print(f"Booking database initialized at: {DB_PATH}")


if __name__ == "__main__":
    initialize_bookings_db()