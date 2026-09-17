from functools import lru_cache
from pathlib import Path

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

CHROMA_PATH = str(Path(__file__).resolve().parent / "chroma_db")


COLLECTION_NAME = "service_rules"


@lru_cache(maxsize=1)
def get_embeddings() -> HuggingFaceEmbeddings:
    """Load the embedding weights once for the lifetime of this process."""
    return HuggingFaceEmbeddings(model_name="BAAI/bge-base-en-v1.5")


def get_retriever(rules: list[str]):
    """Create a filtered retriever using the shared embedding model."""

    embeddings = get_embeddings()

    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_PATH
    )

    return vectorstore.as_retriever(    
        search_kwargs={
            "k": len(rules),
            "filter": {
                "rule": {
                    "$in": rules
                }
            }
        }
    )
