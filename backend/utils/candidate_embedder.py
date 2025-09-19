from llama_index.core.schema import Document
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import Settings
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import VectorStoreIndex
from pymongo import MongoClient
import os, faiss, gridfs
import logging

logger = logging.getLogger(__name__)


def embed_candidate(email, text):
    document = Document(text=text)
    embed_model = HuggingFaceEmbedding(model_name="hkunlp/instructor-xl")
    node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)
    Settings.embed_model = embed_model
    Settings.node_parser = node_parser

    user_index_dir = os.path.join("faiss_index", email)
    logger.info("Index path: %s", user_index_dir)
    index_path = os.path.join(user_index_dir, "index.faiss")
    os.makedirs(user_index_dir, exist_ok=True)

    if os.path.exists(index_path):
        logger.info("Loading existing FAISS index from: %s", index_path)
        faiss_index = faiss.read_index(index_path)
    else:
        logger.info("Creating new FAISS index for: %s", email)
        faiss_index = faiss.IndexFlatL2(768)

    faiss_store = FaissVectorStore(faiss_index=faiss_index)
    index = VectorStoreIndex.from_documents([document], vector_store=faiss_store)
    index.storage_context.persist(persist_dir=user_index_dir)
    faiss.write_index(faiss_index, index_path)

    return index


def store_file_in_mongodb(file_path, email):
    logger.info("Storing file in MongoDB: %s", file_path)
    mongo_uri = os.getenv("MONGO_URI", "mongodb://mongodb:27017/")
    client = MongoClient(mongo_uri)
    db = client[os.getenv("DB_NAME", "candidate_data")]
    fs = gridfs.GridFS(db)
    with open(file_path, "rb") as f:
        file_id = fs.put(f, filename=os.path.basename(file_path), email=email)
    logger.info("File stored with ID: %s", file_id)
    return file_id
