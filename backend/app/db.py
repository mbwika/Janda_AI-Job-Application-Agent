# app/db.py
from pymongo import MongoClient
import os


# Get MongoDB credentials from environment variables
MONGO_HOST = os.getenv("MONGO_HOST", "mongodb")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
MONGO_USER = os.getenv("MONGO_INITDB_ROOT_USERNAME")
MONGO_PASS = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
DB_NAME = os.getenv("DB_NAME", "candidate_data")

if MONGO_USER and MONGO_PASS:
    MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/"
else:
    MONGO_URI = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/"

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

