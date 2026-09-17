def execute_or_escalate(state):
    """Convert the policy decision into the workflow action."""

    # Mandatory escalation takes priority.
    if state.get("escalation_required"):
        return {
            "action": "escalate"
        }

    decision = state.get("action")

    if decision in ["approved", "partially_approved"]:
        return {
            "action": "resolve"
        }

    if decision == "escalate":
        return {
            "action": "escalate"
        }

    return {
        "action": "deny"
    }