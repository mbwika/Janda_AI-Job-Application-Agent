# app/db.py
from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "candidate_data")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

def mongo_has_profile(email: str) -> bool:
    """
    Check if MongoDB has a collection named after the email, and if it contains any documents.
    """
    if email in db.list_collection_names():
        collection = db[email]
        return collection.count_documents({}) > 0
    return False

