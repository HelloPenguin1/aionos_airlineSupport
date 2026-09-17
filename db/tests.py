import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "bookings.db"

#script is anything depending on what i checked

def delete_booking():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()


    cursor.execute("DROP TABLE bookings")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    delete_booking()