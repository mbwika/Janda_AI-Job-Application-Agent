# app/user_profile_utils.py

# from vectorstore import faiss_exists_for_email
# from db import mongo_has_profile

# def check_user_profile(email: str) -> str:
#     """
#     Check whether a user's profile exists in MongoDB and FAISS.
#     Returns 'exists' if found in both, else 'new'.
#     """
#     mongo_ok = mongo_has_profile(email)
#     faiss_ok = faiss_exists_for_email(email)

#     if mongo_ok and faiss_ok:
#         return "exists"
#     return "new"

# app/user_profile_utils.py

"""Compatibility wrapper re-exporting from `backend.utils.user_profile_utils`."""
from backend.utils.user_profile_utils import check_user_profile

__all__ = ["check_user_profile"]
