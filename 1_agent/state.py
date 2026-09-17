from typing import TypedDict, Any


class AgentState(TypedDict, total=False):
    '''State memory for the agents'''
    # Conversation
    user_message: str
    session_id: str

    # Customer identification
    pnr: str

    # Data retrieved from SQLite
    customer: dict
    bookings: list

    # LLM understanding
    intent: str
    requested_action: str
    legal_threat: bool

    # Policy retrieval
    policy_documents: list
    policy_context: str

    # Decision
    action: str
    escalation_required: bool
    escalation_reason: str

    # Final output
    response: str