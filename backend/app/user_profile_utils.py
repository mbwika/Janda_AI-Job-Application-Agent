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

import os
from pymongo import MongoClient
import faiss
import numpy as np

def check_user_profile(email: str) -> bool:
    """Returns True if profile exists in both MongoDB and FAISS."""
    # ✅ MongoDB Check
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    client = MongoClient(mongo_uri)
    db = client["job_data"]
    exists_in_db = db.user_profiles.find_one({"email": email}) is not None

    # ✅ FAISS Check (vector store saved as binary)
    faiss_index_path = f"vector_stores/{email}.index"
    exists_in_faiss = os.path.exists(faiss_index_path)

    return exists_in_db and exists_in_faiss
