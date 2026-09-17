from pathlib import Path

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


CHROMA_PATH = Path(__file__).resolve().parent / "chroma_db"
COLLECTION_NAME = "service_rules"


def search_vector_store(query: str, result_count: int = 3) -> None:
	embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-base-en-v1.5")
	vector_store = Chroma(
		collection_name=COLLECTION_NAME,
		embedding_function=embeddings,
		persist_directory=str(CHROMA_PATH),
	)

	results = vector_store.similarity_search_with_score(query, k=result_count)

	print(f"Database: {CHROMA_PATH}")
	print(f"Collection: {COLLECTION_NAME}")
	print(f"Query: {query}\n")

	for index, (document, score) in enumerate(results, start=1):
		print(f"Result {index} (distance: {score:.4f})")
		print(f"Rule: {document.metadata.get('rule', 'unknown')}")
		print(document.page_content.strip())
		print()


if __name__ == "__main__":
	search_vector_store("What happens when a flight is delayed more than 3 hours?")
