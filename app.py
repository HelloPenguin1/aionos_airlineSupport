"""Minimal Streamlit chat interface for the existing resolution workflow."""

from pathlib import Path
import sqlite3
from uuid import uuid4

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent
CUSTOMERS_DB = PROJECT_ROOT / "data" / "customers.db"


@st.cache_data
def load_customers() -> list[dict[str, str]]:
    with sqlite3.connect(CUSTOMERS_DB) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            "SELECT name, pnr FROM customers ORDER BY name"
        ).fetchall()
    return [dict(row) for row in rows]


@st.cache_resource
def load_workflow():
    from agent.workflow import workflow

    return workflow


@st.cache_resource
def warm_policy_retrieval() -> None:
    """Load model weights at app startup, before the first customer request."""
    from rag.retriever import get_embeddings

    get_embeddings()


def initialise_session() -> None:
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("session_id", str(uuid4()))


def new_conversation() -> None:
    st.session_state.messages = []
    st.session_state.session_id = str(uuid4())


def visible_resolution(result: dict) -> dict:
    """Return observable decision fields; never expose prompts or hidden reasoning."""
    return {
        "Intent": result.get("intent"),
        "Requested actions": result.get("requested_action"),
        "Rules used": result.get("source_rules", result.get("rules", [])),
        "Decision / action": result.get("action"),
        "Allowed actions": result.get("allowed_actions", []),
        "Denied actions": result.get("denied_actions", []),
        "Escalation required": result.get("escalation_required", False),
        "Escalation reason": result.get("escalation_reason", ""),
    }


def submit_message(prompt: str, pnr: str) -> None:
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        result = load_workflow().invoke(
            {
                "user_message": prompt,
                "pnr": pnr,
                "session_id": st.session_state.session_id,
            }
        )
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": result.get("response")
                or "The agent did not return a customer response.",
                "resolution": visible_resolution(result),
            }
        )
    except Exception as error:
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": "I’m unable to process that request right now. Please try again.",
                "debug_error": str(error),
            }
        )


st.set_page_config(
    page_title="Airline Customer Resolution Agent",
    page_icon=":material/support_agent:",
    layout="centered",
)
initialise_session()

customers = load_customers()
if not customers:
    st.error("No customers are available. Initialise the customer database first.")
    st.stop()

customer_options = {
    f"{customer['name']} — {customer['pnr']}": customer for customer in customers
}

with st.sidebar:
    selected_label = st.selectbox("Customer", list(customer_options), key="customer")
    selected_customer = customer_options[selected_label]
    st.caption(f"PNR: `{selected_customer['pnr']}`")
    if st.button("New conversation", icon=":material/add_comment:", width="stretch"):
        new_conversation()
        st.rerun()

st.title("Airline Customer Resolution Agent", icon=":material/support_agent:")
st.caption("AI-powered disruption resolution prototype")

# This runs before the chat input appears. All later retrievals reuse these weights.
try:
    with st.spinner("Preparing policy retrieval…"):
        warm_policy_retrieval()
except Exception:
    st.warning("Policy retrieval could not be prepared. Please check the local model setup.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if message.get("resolution"):
            with st.expander("Resolution output", expanded=True, icon=":material/fact_check:"):
                st.json(message["resolution"], expanded=False)
        if message.get("debug_error"):
            with st.expander("Debug information", icon=":material/bug_report:"):
                st.code(message["debug_error"], language="text")

prompt = st.chat_input("Describe the disruption or ask for support", submit_mode="disable")
if prompt:
    submit_message(prompt, selected_customer["pnr"])
    st.rerun()
