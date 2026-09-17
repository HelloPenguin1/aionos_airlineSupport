from typing import TypedDict


class AgentState(TypedDict, total=False):
    '''State memory for the agents'''
    # Conversation
    user_message: str
    session_id: str

    # Customer identification
    pnr: str
    pnr_valid: bool

    # Data retrieved from SQLite
    customer: dict
    bookings: list

    # LLM understanding
    intent: str
    requested_action: str
    rules: list
    legal_threat: bool

    # Policy retrieval
    policy_documents: list
    policy_context: str

    # Decision
    action: str
    allowed_actions: list
    denied_actions: list
    escalation_required: bool
    escalation_reason: str
    source_rules: list

    # Final output
    response: str

    # Audit
    audit_record: dict