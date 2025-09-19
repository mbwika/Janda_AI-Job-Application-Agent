"""Compatibility wrapper re-exporting from `backend.utils.vectorstore`."""
from backend.utils.vectorstore import faiss_exists_for_email

__all__ = ["faiss_exists_for_email"]
