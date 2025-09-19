import os
import pickle

VECTOR_INDEX_PATH = os.getenv("VECTOR_INDEX_PATH", "faiss_index")
METADATA_STORE_PATH = os.getenv("METADATA_STORE_PATH", "metadata.pkl")


def faiss_exists_for_email(email: str) -> bool:
    """Check if FAISS vector store contains a vector associated with the given email."""
    if not os.path.exists(VECTOR_INDEX_PATH) or not os.path.exists(METADATA_STORE_PATH):
        return False

    with open(METADATA_STORE_PATH, "rb") as f:
        metadata = pickle.load(f)

    return any(entry.get("email") == email for entry in metadata)
