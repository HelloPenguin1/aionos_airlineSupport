from typing import Literal

from pydantic import BaseModel, Field


# Policy categories available in the service-rules knowledge base
Rule = Literal[
    "cancellation",
    "delay",
    "refund",
    "fare_difference",
    "loyalty",
    "escalation",
]


class RequestAnalysis(BaseModel):
    """Structured representation of the customer's request."""

    intent: str = Field(
        description="The main intent of the customer's request."
    )

    requested_actions: list[str] = Field(
        description="Specific actions the customer is asking the airline to take."
    )

    rules: list[Rule] = Field(
        description=(
            "Relevant service-policy categories for this request. "
            "Select only from the allowed rule categories."
        )
    )

    legal_threat: bool = Field(
        description=(
            "Whether the customer has made a legal threat or explicitly "
            "requested an immediate formal/legal complaint."
        )
    )

    unclear_request: bool = Field(
        description="Whether the customer's requested action is unclear."
    )


class PolicyDecision(BaseModel):
    """Structured decision after evaluating the request against airline policy."""

    decision: Literal[
        "approved",
        "partially_approved",
        "denied",
        "escalate",
    ] = Field(
        description="Overall policy decision for the customer's request."
    )

    allowed_actions: list[str] = Field(
        description="Actions explicitly allowed by the supplied airline policy."
    )

    denied_actions: list[str] = Field(
        description="Requested actions that are not allowed by the supplied policy."
    )

    escalation_required: bool = Field(
        description="Whether the request requires human or supervisor escalation."
    )

    escalation_reason: str = Field(
        description=(
            "Reason for escalation. Use an empty string when escalation "
            "is not required."
        )
    )

    source_rules: list[str] = Field(
        description="Policy rule categories used to make the decision."
    )