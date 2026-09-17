from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from pathlib import Path

CHROMA_PATH = str(Path(__file__).resolve().parent / "chroma_db")


COLLECTION_NAME = "service_rules"


def get_retriever(rules: list[str]):

    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-base-en-v1.5"
    )

    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_PATH
    )

    print("RULES:", rules)
    print("COLLECTION COUNT:", vectorstore._collection.count())
    print("COLLECTION DATA:")
    print(vectorstore._collection.get(include=["metadatas"]))

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