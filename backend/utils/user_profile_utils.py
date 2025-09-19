import os
from pymongo import MongoClient


def check_user_profile(email: str) -> bool:
    """Returns True if profile exists in both MongoDB and FAISS."""
    mongo_uri = os.getenv("MONGO_URI", "mongodb://mongodb:27017/")
    client: MongoClient = MongoClient(mongo_uri)
    db_name = os.getenv("DB_NAME", "job_data")
    db = client[db_name]
    exists_in_db = db.user_profiles.find_one({"email": email}) is not None

    # FAISS check
    faiss_index_path = f"vector_stores/{email}.index"
    exists_in_faiss = os.path.exists(faiss_index_path)

    return exists_in_db and exists_in_faiss
