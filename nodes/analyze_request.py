from langchain_groq import ChatGroq

from nodes.structured_output import RequestAnalysis
from nodes.prompts import REQUEST_ANALYSIS_PROMPT
import os

llm = ChatGroq(
    model_name="openai/gpt-oss-20b",
    temperature=0,
    groq_api_key=os.getenv("GROQ_API_KEY"),
    max_tokens=500
)


def analyze_request(state):
    """Analyze the customer's message and extract structured request information."""

    prompt = REQUEST_ANALYSIS_PROMPT.format(
        user_message=state["user_message"]
    )

    structured_llm = llm.with_structured_output(RequestAnalysis,
                                                method="json_schema")

    result = structured_llm.invoke(prompt)

    print("REQUEST ANALYSIS:", result)
    print("RULES:", result.rules)
    
    return {
        "intent": result.intent,
        "requested_action": ", ".join(result.requested_actions),
        "rules": result.rules,
        "legal_threat": result.legal_threat,
    }