"""Compatibility wrapper re-exporting from `backend.utils.candidate_embedder`."""
from backend.utils.candidate_embedder import embed_candidate, store_file_in_mongodb

__all__ = ["embed_candidate", "store_file_in_mongodb"]