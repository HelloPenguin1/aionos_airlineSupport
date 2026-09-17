

def immediate_escalation_check(state):
    """Check whether the request requires immediate escalation."""

    if state.get("legal_threat", False):
        return {
            "escalation_required": True,
            "escalation_reason": (
                "Customer has made a legal threat or requested "
                "an immediate formal complaint."
            ),
            "action": "escalate",
        }

    return {
        "escalation_required": False
    }