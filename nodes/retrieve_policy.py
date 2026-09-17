from rag.retriever import get_retriever


def retrieve_policy(state):
    """Retrieve the relevant service policies from ChromaDB."""

    rules = state.get("rules", [])

    if not rules:
        return {
            "policy_documents": [],
            "policy_context": "",
        }

    #builds the retriever with relevant documetns
    retriever = get_retriever(rules)

    documents = retriever.invoke(
        state["user_message"]
    )

    policy_context = "\n\n".join(
        f"RULE: {doc.metadata.get('rule')}\n"
        f"{doc.page_content}"
        for doc in documents
    )

    return {
        "policy_documents": documents,
        "policy_context": policy_context,
    }