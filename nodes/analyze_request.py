from langchain_groq import ChatGroq

from nodes.structured_output import RequestAnalysis
from nodes.prompts import REQUEST_ANALYSIS_PROMPT


llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)


def analyze_request(state):
    """Analyze the customer's message and extract structured request information."""

    prompt = REQUEST_ANALYSIS_PROMPT.format(
        user_message=state["user_message"]
    )

    structured_llm = llm.with_structured_output(RequestAnalysis)

    result = structured_llm.invoke(prompt)

    return {
        "intent": result.intent,
        "requested_action": ", ".join(result.requested_actions),
        "rules": result.rules,
        "legal_threat": result.legal_threat,
    }