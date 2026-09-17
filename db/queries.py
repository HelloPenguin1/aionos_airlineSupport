import sqlite3
from pathlib import Path

CUSTOMERS_DB = Path(__file__).parent.parent / "data" / "customers.db"
BOOKINGS_DB  = Path(__file__).parent.parent / "data" / "bookings.db"


def get_customer_by_pnr(pnr):
    '''Get customer details from PNR number, including travel history via join function'''
    conn = sqlite3.connect(CUSTOMERS_DB)
    conn.row_factory = sqlite3.Row

    customer = conn.execute("""
        SELECT c.*, 
               t.flights_last_12_months,
               t.prior_complaints,
               t.complaint_details
        FROM customers c
        LEFT JOIN travel_history t 
            ON c.id = t.customer_id
        WHERE c.pnr = ?
    """, (pnr,)).fetchone()

    conn.close()

    return dict(customer) if customer else None


def get_bookings_by_pnr(pnr):
    conn = sqlite3.connect(BOOKINGS_DB)
    conn.row_factory = sqlite3.Row

    bookings = conn.execute("""
        SELECT *
        FROM bookings
        WHERE pnr = ?
    """, (pnr,)).fetchall()

    conn.close()

    return [dict(booking) for booking in bookings]



#testing
if __name__ == "__main__":
    customer = get_customer_by_pnr("SK4821X")
    print("CUSTOMER:")
    print(customer)

    bookings = get_bookings_by_pnr("SK4821X")
    print("\nBOOKINGS:")
    for booking in bookings:
        print(booking)