from langchain_openai import ChatOpenAI

from prompts import RESPONSE_PROMPT


llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
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