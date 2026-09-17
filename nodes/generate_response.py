from langchain_groq import ChatGroq

from nodes.prompts import RESPONSE_PROMPT
import os

llm = ChatGroq(
    model_name="qwen/qwen3.8-27b",
    temperature=0,
    groq_api_key=os.getenv("GROQ_API_KEY")
)


def generate_response(state):
    """Generate the final customer-facing response."""

    prompt = RESPONSE_PROMPT.format(
        customer=state.get("customer", {}),
        bookings=state.get("bookings", []),
        user_message=state["user_message"],
        action=state.get("action", ""),
        allowed_actions=state.get("allowed_actions", []),
        denied_actions=state.get("denied_actions", []),
        escalation_required=state.get("escalation_required", False),
        escalation_reason=state.get("escalation_reason", ""),
        source_rules=state.get("source_rules", []),
    )

    response = llm.invoke(prompt)

    return {
        "response": response.content
    }

