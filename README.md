# Airline Customer Resolution Agent

A local demonstration of an airline-support agent that interprets a passenger request, retrieves the relevant airline policy, evaluates the request against passenger and booking context, and returns a resolution, denial, or escalation outcome.

The application uses fictional, pre-seeded customer, booking, and policy data. It does not connect to live airline, ticketing, CRM, or payment systems.

## Run the application

1. Create a `.env` file in the project root with a valid Groq API key:

   ```env
   GROQ_API_KEY=your_key_here
   ```

2. Install dependencies and start Streamlit:

   ```bash
   uv sync
   uv run streamlit run app.py
   ```

3. Select a demo customer in the sidebar and submit a support request.

The first run may take longer while the HuggingFace embedding model is loaded.

## Technology stack

| Concern | Technology used |
| --- | --- |
| User interface | Streamlit |
| Application language | Python 3.12+ |
| Workflow orchestration | LangGraph |
| LLM integration and prompting | LangChain / LangChain Core |
| Request analysis | Groq `openai/gpt-oss-20b` |
| Decision and response generation | Groq `openai/gpt-oss-120b` |
| Structured LLM output | Pydantic JSON-schema models |
| Embeddings | HuggingFace Sentence Transformers, `BAAI/bge-base-en-v1.5` |
| Vector database | ChromaDB, persisted locally in `rag/chroma_db/` |
| Operational data | SQLite (`data/customers.db` and `data/bookings.db`) |
| Configuration | `python-dotenv` |

## Four main components

### 1. Application layer

[`app.py`](app.py) is the Streamlit chat application. It loads demo customers, creates a session ID for each conversation, invokes the compiled LangGraph workflow, and displays the customer-facing response, observable decision fields, and retrieved policy context. The UI does not make policy or escalation decisions.

### 2. Agent orchestration layer

[`agent/workflow.py`](agent/workflow.py) builds the LangGraph `StateGraph`; [`agent/state.py`](agent/state.py) defines the shared `AgentState`; and [`nodes/`](nodes) contains the focused workflow steps and prompts. The graph carries customer context, extracted intent, policy evidence, decision fields, response, and audit record between nodes.

### 3. Database layer

The project uses two local SQLite databases:

| Database | Contents | Access |
| --- | --- | --- |
| `data/customers.db` | Demo passengers, loyalty tier, contact fields, and travel history | `get_customer_by_pnr()` in [`db/queries.py`](db/queries.py) |
| `data/bookings.db` | Demo bookings: PNR, flight, route, date, departure time, and disruption status | `get_bookings_by_pnr()` in [`db/queries.py`](db/queries.py) |

[`db/init_customers.py`](db/init_customers.py) and [`db/init_bookings.py`](db/init_bookings.py) define and seed these datasets. The customer schema also defines an `audit_logs` table, but the current [`record_action`](nodes/record_action.py) node returns an audit record in graph state only; it does **not** insert it into SQLite.

### 4. RAG layer

The retrieval-augmented generation (RAG) layer grounds policy evaluation in locally indexed service rules. [`rag/ingest.py`](rag/ingest.py) creates policy `Document` objects, embeds them, and persists them in the Chroma collection named `service_rules`. At runtime, [`rag/retriever.py`](rag/retriever.py) loads the embedding model once per process and creates a Chroma retriever filtered to the policy categories selected during request analysis.

The retrieved text is supplied as `policy_context` to the policy-decision model, whose prompt restricts policy reasoning to that context.

## Workflow architecture

```text
START
  |
  v
load_customer_context
  |
  v
analyze_request
  |
  v
immediate_escalation_check
  |\
  | \-- legal threat / formal complaint --> generate_response
  |                                            |
  |                                            v
  |                                        record_action --> END
  |
  \-- all other requests --> retrieve_policy
                                |
                                v
                          evaluate_request
                                |
                                v
                         execute_or_escalate
                                |
                                v
                          generate_response
                                |
                                v
                           record_action --> END
```

The only conditional route is after the immediate-escalation check. A request marked as a legal threat or immediate formal complaint skips RAG and policy evaluation. All other requests retrieve category-filtered policy evidence before the workflow decides whether to resolve, deny, or escalate.

## Nodes: functions and outputs

| Node | Function | State fields it outputs |
| --- | --- | --- |
| `load_customer_context` | Looks up the supplied PNR in the customer and booking SQLite databases. | `pnr_valid`, `customer`, `bookings`; for a missing or unknown PNR it also returns a `response` message. |
| `analyze_request` | Uses structured LLM output to interpret only the customer message: intent, requested actions, applicable policy categories, and legal-threat/formal-complaint status. | `intent`, `requested_action`, `rules`, `legal_threat` |
| `immediate_escalation_check` | Applies the early safety gate for `legal_threat`. | Either `escalation_required: true`, `escalation_reason`, and `action: "escalate"`; or `escalation_required: false`. |
| `retrieve_policy` | Retrieves Chroma documents filtered by `rules` and serializes them into policy evidence. | `policy_documents`, `policy_context` |
| `evaluate_request` | Uses structured LLM output to assess customer data, bookings, request, and policy evidence. | `action` (`approved`, `partially_approved`, `denied`, or `escalate`), `allowed_actions`, `denied_actions`, `escalation_required`, `escalation_reason`, `source_rules` |
| `execute_or_escalate` | Maps the policy decision to the final operational outcome. Escalation takes priority; approved and partially approved decisions resolve; all other decisions deny. | `action` (`resolve`, `escalate`, or `deny`) |
| `generate_response` | Produces the concise customer-facing reply from the final action, decision fields, customer, and booking context. | `response` |
| `record_action` | Creates a structured trace of the completed interaction in graph state. | `audit_record` containing `pnr`, `intent`, `action`, `escalation_required`, and `escalation_reason` |

## What the RAG vector database contains

The persistent Chroma collection `service_rules` contains six fictional airline-policy documents. Each document uses `source: "Service Rules"` and a `rule` metadata field for category filtering.

| `rule` metadata | Policy content indexed in ChromaDB |
| --- | --- |
| `cancellation` | For airline-cancelled flights, choose free rebooking on the next available flight within 24 hours or a full refund. |
| `delay` | Under three hours: ₹500 meal voucher. Over three hours: meal voucher and lounge access. Over five hours: those benefits plus hotel accommodation for delayed hours, not a full night. |
| `refund` | Airline-caused cancellations receive a full refund within seven business days to the original payment method. |
| `fare_difference` | Customers choosing a higher-fare rebooking option pay the difference; agents need supervisor approval to waive more than ₹1,500. |
| `loyalty` | Gold and Platinum customers receive priority rebooking, but no compensation beyond the standard disruption policy. |
| `escalation` | Escalate compensation beyond policy, fare-difference waivers over ₹1,500, non-airline-caused disruption exceptions, legal threats/formal complaints, and refunds to a different payment method. |

For a request classified with one or more rules, the retriever asks Chroma for `k = len(rules)` documents and filters candidates to those categories. When no policy category is selected, it returns an empty policy context.

## Project layout

```text
.
├── app.py                    # Streamlit interface
├── agent/
│   ├── state.py               # Shared LangGraph state
│   └── workflow.py            # Graph definition and routing
├── nodes/                     # Individual graph nodes, prompts, schemas
├── db/
│   ├── init_customers.py      # Customer/travel-history/audit schema and seed data
│   ├── init_bookings.py       # Booking schema and seed data
│   └── queries.py             # SQLite reads used by the graph
├── data/
│   ├── customers.db
│   └── bookings.db
└── rag/
    ├── ingest.py              # Policy documents and Chroma ingestion
    ├── retriever.py           # Runtime category-filtered retrieval
    └── chroma_db/             # Persistent Chroma collection
```

## Scope and Assumptions

- All passengers, flights, and policies are local demo data.
- The agent suggests outcomes; it does not rebook flights, issue refunds, send escalations, or contact customers.
- A valid Groq API key is required, along with local access to the embedding model files or download source.
- Rebuild the Chroma collection with `rag/ingest.py` if `rag/chroma_db/` is missing or needs regeneration.

## For Demo, click the link under github repository description