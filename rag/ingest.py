from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import os
from dotenv import load_dotenv
load_dotenv()



CHROMA_PATH = "rag/chroma_db"
COLLECTION_NAME = "service_rules"


def create_policy_documents():
    documents = [
        Document(
            page_content="""
            Cancellation Policy:
            If the airline cancels a flight, the customer can choose either:
            1. Free rebooking on the next available flight within 24 hours, or
            2. A full refund.
            """,
            metadata={
                "source": "Service Rules",
                "rule": "cancellation"
            }
        ),

        Document(
            page_content="""
            Delay Policy:
            For delays under 3 hours, provide a ₹500 meal voucher.

            For delays greater than 3 hours, provide a meal voucher and lounge access.

            For delays greater than 5 hours, provide a meal voucher, lounge access,
            and hotel accommodation covering the delayed hours. The hotel does not
            cover full night's stay.
            """,
            metadata={
                "source": "Service Rules",
                "rule": "delay"
            }
        ),

        Document(
            page_content="""
            Refund Policy:
            For airline-caused cancellations, refunds are issued in full within
            7 business days and must be returned to the original payment method.
            """,
            metadata={
                "source": "Service Rules",
                "rule": "refund"
            }
        ),

        Document(
            page_content="""
            Fare Difference Policy:
            If a customer voluntarily chooses a higher-fare rebooking option,
            the customer must pay the fare difference.

            Agents cannot waive a fare difference greater than ₹1,500 without
            supervisor approval.
            """,
            metadata={
                "source": "Service Rules",
                "rule": "fare_difference"
            }
        ),

        Document(
            page_content="""
            Loyalty Policy:
            Gold and Platinum customers receive priority rebooking.

            Loyalty status does not provide additional compensation beyond the
            standard disruption policy.
            """,
            metadata={
                "source": "Service Rules",
                "rule": "loyalty"
            }
        ),

        Document(
            page_content="""
            Escalation Policy:
            The agent must escalate requests for compensation beyond the supplied
            policy.

            The agent must escalate requests to waive a fare difference greater
            than ₹1,500.

            Exceptions for disruptions that were not caused by the airline must
            be escalated.

            Legal threats or formal complaints must be escalated immediately.

            Refunds to a payment method different from the original payment
            method must be escalated.
            """,
            metadata={
                "source": "Service Rules",
                "rule": "escalation"
            }
        ),
    ]

    return documents


def create_vector_store():
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-base-en-v1.5",    
    )
    
    documents = create_policy_documents()

    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_PATH
    )

    print(f"Stored {len(documents)} policy documents in ChromaDB.")
    return vectorstore


if __name__ == "__main__":
    create_vector_store()
    