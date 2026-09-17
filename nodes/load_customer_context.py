from db.queries import get_customer_by_pnr, get_bookings_by_pnr


def load_customer_context(state):
    """Load customer and booking information using the PNR."""

    pnr = state.get("pnr")

    if not pnr:
        return {
            "pnr_valid": False,
            "customer": None,
            "bookings": [],
            "response": "Please provide a valid PNR."
        }

    customer = get_customer_by_pnr(pnr)
    bookings = get_bookings_by_pnr(pnr)

    if customer is None:
        return {
            "pnr_valid": False,
            "customer": None,
            "bookings": [],
            "response": (
                "I could not find that PNR. "
                "Please check the PNR and try again."
            )
        }

    return {
        "pnr_valid": True,
        "customer": customer,
        "bookings": bookings,
    }