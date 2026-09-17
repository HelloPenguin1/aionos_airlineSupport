def record_action(state):
    """Create an audit record for the completed support interaction."""

    audit_record = {
        "pnr": state.get("pnr"),
        "intent": state.get("intent"),
        "action": state.get("action"),
        "escalation_required": state.get(
            "escalation_required",
            False
        ),
        "escalation_reason": state.get(
            "escalation_reason",
            ""
        ),
    }

    return {
        "audit_record": audit_record
    }