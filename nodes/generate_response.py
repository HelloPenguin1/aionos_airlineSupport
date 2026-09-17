from langchain_groq import ChatGroq

from nodes.prompts import RESPONSE_PROMPT
import os

llm = ChatGroq(
    model_name="openai/gpt-oss-120b",
    temperature=0.3,
    groq_api_key=os.getenv("GROQ_API_KEY"),
    max_tokens=300
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

