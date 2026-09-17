from dotenv import load_dotenv

load_dotenv()

from langgraph.graph import StateGraph, START, END

from agent.state import AgentState

from nodes.load_customer_context import load_customer_context
from nodes.analyze_request import analyze_request
from nodes.immediate_escalation_check import immediate_escalation_check
from nodes.retrieve_policy import retrieve_policy
from nodes.evaluate_request import evaluate_request
from nodes.execute_or_escalate import execute_or_escalate
from nodes.generate_response import generate_response
from nodes.record_action import record_action


def route_after_escalation_check(state: AgentState):
    """
    Decide whether the request should bypass policy retrieval.

    Legal threats and formal complaints must be escalated immediately.
    All other requests continue through policy retrieval.
    """
    if state.get("escalation_required", False):
        return "generate_response"

    return "retrieve_policy"


def build_workflow():
    """Build and compile the customer resolution workflow."""

    graph = StateGraph(AgentState)

    # --------------------------------------------------------
    # Add nodes
    # --------------------------------------------------------

    graph.add_node(
        "load_customer_context",
        load_customer_context
    )

    graph.add_node(
        "analyze_request",
        analyze_request
    )

    graph.add_node(
        "immediate_escalation_check",
        immediate_escalation_check
    )

    graph.add_node(
        "retrieve_policy",
        retrieve_policy
    )

    graph.add_node(
        "evaluate_request",
        evaluate_request
    )

    graph.add_node(
        "execute_or_escalate",
        execute_or_escalate
    )

    graph.add_node(
        "generate_response",
        generate_response
    )

    graph.add_node(
        "record_action",
        record_action
    )

    # --------------------------------------------------------
    # Main workflow
    # --------------------------------------------------------

    graph.add_edge(
        START,
        "load_customer_context"
    )

    graph.add_edge(
        "load_customer_context",
        "analyze_request"
    )

    graph.add_edge(
        "analyze_request",
        "immediate_escalation_check"
    )

    # Legal/formal complaint requests bypass RAG and
    # go directly to the response stage.
    graph.add_conditional_edges(
        "immediate_escalation_check",
        route_after_escalation_check,
        {
            "retrieve_policy": "retrieve_policy",
            "generate_response": "generate_response",
        }
    )

    graph.add_edge(
        "retrieve_policy",
        "evaluate_request"
    )

    graph.add_edge(
        "evaluate_request",
        "execute_or_escalate"
    )

    graph.add_edge(
        "execute_or_escalate",
        "generate_response"
    )

    graph.add_edge(
        "generate_response",
        "record_action"
    )

    graph.add_edge(
        "record_action",
        END
    )

    return graph.compile()


workflow = build_workflow()