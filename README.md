# Customer Resolution Agent

An agentic customer-service workflow that uses LangGraph to analyze
customer requests, retrieve relevant policies, decide whether a request
can be resolved automatically, execute permitted actions, and maintain
an audit trail.

## Run the reviewer UI

From the project root, ensure the existing `.env` includes `GROQ_API_KEY`,
then start the Streamlit prototype:

```bash
uv run streamlit run app.py
```

The sidebar provides the three supplied demo scenarios. The interface only
displays state returned by the existing LangGraph workflow; it does not make
policy or escalation decisions itself.

## Architecture

The system is organized into four main layers:

1.  **Application layer** --- Streamlit interface in `app.py`
2.  **Agent orchestration layer** --- LangGraph workflow, state, nodes,
    and prompts
3.  **Tool/data layer** --- Customer and booking lookups plus customer
    actions
4.  **Policy/RAG layer** --- Policy ingestion, ChromaDB retrieval, and
    policy-grounded evaluation

### End-to-end flow

``` text
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
  |
  +------------------------------+
  |                              |
  | No immediate escalation      | Policy required
  |                              |
  |                              v
  |                       retrieve_policy
  |                              |
  |                              v
  |                       evaluate_request
  |                              |
  |                              v
  |                       execute_or_escalate
  |                              |
  +---------------+--------------+
                  |
                  v
          generate_response
                  |
                  v
           record_action
                  |
                  v
                 END
```

The escalation check acts as an early safety gate. Requests requiring
immediate escalation, such as legal threats or formal complaints, can
bypass normal automated resolution. Other requests continue through
policy retrieval and evaluation before the system either resolves the
request or escalates it.

## Core Workflow

### 1. Customer context

`load_customer_context` retrieves relevant customer information from the
customer database.

Customer context can be combined with booking information so later
decisions are made using the actual customer and reservation state
rather than only the user's message.

### 2. Request analysis

`analyze_request` uses the LLM to interpret the user's request and
determine the type of operation required.

This separates natural-language understanding from deterministic tools
such as database lookups and action execution.

### 3. Immediate escalation check

`immediate_escalation_check` is an early decision gate.

Examples include:

-   Legal threats
-   Formal complaints
-   Requests that require human intervention
-   Other cases defined as mandatory escalation conditions

This prevents the agent from attempting normal automated resolution when
escalation should happen immediately.

### 4. Policy retrieval

For requests that require policy-based reasoning, `retrieve_policy`
queries the policy knowledge base.

The supplied policies are ingested into ChromaDB through
`rag/ingest.py`, while `rag/retriever.py` handles retrieval during the
agent workflow.

### 5. Request evaluation

`evaluate_request` combines:

-   Customer context
-   Booking information
-   Retrieved policy
-   Request interpretation

The result determines whether the request is permitted and what action
should be taken.

### 6. Execute or escalate

`execute_or_escalate` is the action decision point.

Depending on the evaluation, the system can:

-   Execute an allowed action
-   Escalate the request to a human
-   Avoid taking an unsupported or unauthorized action

Actions are implemented through `tools/action_tools.py`.

### 7. Response generation

`generate_response` converts the workflow result into the final
user-facing response.

The response should reflect the actual action taken or escalation
decision rather than independently inventing an outcome.

### 8. Audit logging

`record_action` records the action taken so that the workflow has an
audit trail.

This is important for customer-service systems because an agent should
be able to explain what happened after a request was processed.

## Project Structure

``` text
customer-resolution-agent/
│
├── app.py
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
├── README.md
│
├── data/
│   ├── customers.db
│   └── bookings.db
│
├── db/
│   ├── init_customers.py
│   ├── init_bookings.py
│   └── queries.py
│
├── agent/
│   ├── graph.py
│   ├── state.py
│   ├── nodes.py
│   └── prompts.py
│
├── tools/
│   ├── customer_tools.py
│   ├── booking_tools.py
│   └── action_tools.py
│
├── rag/
│   ├── ingest.py
│   ├── retriever.py
│   └── chroma_db/
│
└── outputs/
    └── screenshots/
```

## Key Files

### Application

#### `app.py`

Streamlit entry point for the application.

Responsibilities:

-   Provides the user interface
-   Accepts customer requests
-   Starts the LangGraph workflow
-   Displays the agent's response and workflow result

------------------------------------------------------------------------

### Agent

#### `agent/graph.py`

Defines the LangGraph workflow and connects the individual nodes.

It controls the execution order and conditional routing between:

-   PNR validation
-   Customer loading
-   Request analysis
-   Immediate escalation checking
-   Policy retrieval
-   Policy evaluation
-   Execution/escalation
-   Response generation
-   Action recording

This file is the central orchestration layer.

#### `agent/state.py`

Defines the shared `AgentState` passed between LangGraph nodes.

The state acts as the workflow's working memory and can contain
information such as:

-   User request
-   Customer information
-   Booking information
-   Request classification
-   Retrieved policy context
-   Evaluation result
-   Action taken
-   Escalation status
-   Final response

#### `agent/nodes.py`

Contains the implementation of the individual workflow nodes.

Rather than putting the entire workflow into one function, each node
performs one focused operation. `graph.py` then composes those
operations into the executable graph.

#### `agent/prompts.py`

Contains system prompts and LLM instructions.

Keeping prompts separate from workflow logic makes the agent easier to
modify and maintain without changing the graph implementation.

------------------------------------------------------------------------

### Tools

#### `tools/customer_tools.py`

Provides customer-related operations, primarily retrieving customer
information.

The tools abstract database access from the agent nodes.

#### `tools/booking_tools.py`

Handles booking and PNR-related operations.

Typical responsibilities include:

-   Validating a PNR
-   Looking up booking information
-   Retrieving flight/reservation details

The underlying booking data is stored in `data/bookings.db`.

#### `tools/action_tools.py`

Contains executable customer-service actions and escalation operations.

Examples include:

-   Refund
-   Rebooking
-   Hotel-related actions
-   Human escalation

Keeping actions in a dedicated tool module creates a boundary between
**deciding what to do** and **actually doing it**.

------------------------------------------------------------------------

### Database

#### `db/init_customers.py`

Creates and seeds the customer SQLite database.

The resulting database is stored at:

``` text
data/customers.db
```

#### `db/init_bookings.py`

Creates and seeds the booking SQLite database.

The resulting database is stored at:

``` text
data/bookings.db
```

#### `db/queries.py`

Contains reusable database access functions.

This prevents SQL/database logic from being duplicated throughout the
agent and tool implementations.

------------------------------------------------------------------------

### RAG / Policy Layer

#### `rag/ingest.py`

Loads the supplied policy documents, processes them for retrieval, and
stores the resulting representations in ChromaDB.

This is the offline/indexing side of the policy RAG pipeline.

#### `rag/retriever.py`

Provides policy retrieval during runtime.

The agent uses this layer when a request requires policy-based
evaluation.

#### `rag/chroma_db/`

Local persistent ChromaDB storage containing the indexed policy
knowledge base.

It allows policy retrieval without rebuilding the vector store for every
application run.

------------------------------------------------------------------------

### Configuration

#### `.env`

Stores environment-specific configuration and secrets.

Secrets should not be committed to version control.

#### `.env.example`

Template showing which environment variables are required without
exposing actual credentials.

#### `requirements.txt`

Defines the Python dependencies required to install and run the project.

#### `.gitignore`

Specifies files and directories that should not be committed to Git,
such as environment files, local databases, caches, and generated
artifacts.

------------------------------------------------------------------------

## Data and Control Flow

``` text
                    ┌─────────────────────┐
                    │      Streamlit      │
                    │       app.py        │
                    └──────────┬──────────┘
                               │
                               v
                    ┌─────────────────────┐
                    │   LangGraph Agent   │
                    │    agent/graph.py   │
                    └──────────┬──────────┘
                               │
             ┌─────────────────┼──────────────────┐
             │                 │                  │
             v                 v                  v
      Customer Tools     Booking Tools       Policy RAG
             │                 │                  │
             v                 v                  v
       customers.db       bookings.db          ChromaDB
             │                 │                  │
             └─────────────────┼──────────────────┘
                               │
                               v
                    ┌─────────────────────┐
                    │ Request Evaluation  │
                    │ + Action Decision   │
                    └──────────┬──────────┘
                               │
                       ┌───────┴────────┐
                       │                │
                       v                v
                    Execute          Escalate
                       │                │
                       └───────┬────────┘
                               v
                    ┌─────────────────────┐
                    │ Generate Response   │
                    └──────────┬──────────┘
                               v
                    ┌─────────────────────┐
                    │   Record Action     │
                    └─────────────────────┘
```

## Design Principles

### Separation of concerns

The project separates orchestration, LLM reasoning, tools, database
access, and retrieval.

This makes each component independently testable and reduces coupling.

### Policy-grounded decisions

The agent does not rely only on the LLM's general knowledge for
customer-service policy decisions. Relevant policy information is
retrieved from the local policy knowledge base and supplied to the
evaluation step.

### Deterministic tool execution

Database lookups and customer actions are implemented as explicit tools
rather than asking the LLM to directly manipulate databases or invent
action results.

### Conditional agent routing

The workflow is not a linear LLM chain. LangGraph provides conditional
routing so requests can follow different paths depending on escalation
requirements and policy evaluation.

### Auditability

The final action is recorded after processing. This provides a trace of
what the system actually did.

## Technology Stack

  Component                  Technology
  -------------------------- ------------
  UI                         Streamlit
  Agent orchestration        LangGraph
  LLM reasoning              LLM API
  Policy retrieval           RAG
  Vector database            ChromaDB
  Customer/booking storage   SQLite
  Backend language           Python



## Architectural Summary

The system combines **agent orchestration, structured customer/booking
data, policy RAG, explicit action tools, conditional escalation, and
audit logging** into a single customer-resolution workflow.

The key architectural distinction is that the LLM is responsible for
understanding and reasoning over the request, while external tools and
the workflow graph control access to customer data, policies, and
real-world actions.
