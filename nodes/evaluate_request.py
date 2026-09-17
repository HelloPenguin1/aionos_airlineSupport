from langchain_groq import ChatGroq

from nodes.structured_output import PolicyDecision
from nodes.prompts import DECISION_PROMPT
import os

llm = ChatGroq(
    model_name="qwen/qwen3.8-27b",
    temperature=0,
    groq_api_key=os.getenv("GROQ_API_KEY")
)


def evaluate_request(state):
    """Evaluate the customer's request against the retrieved airline policy."""

    prompt = DECISION_PROMPT.format(
        customer=state.get("customer", {}),
        bookings=state.get("bookings", []),
        user_message=state["user_message"],
        policy_context=state.get("policy_context", ""),
    )

    structured_llm = llm.with_structured_output(PolicyDecision)

    result = structured_llm.invoke(prompt)

    return {
        "action": result.decision,
        "allowed_actions": result.allowed_actions,
        "denied_actions": result.denied_actions,
        "escalation_required": result.escalation_required,
        "escalation_reason": result.escalation_reason,
        "source_rules": result.source_rules,
    }