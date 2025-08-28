

# candidate_embedder.py

from llama_index.core.schema import Document
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import Settings
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import VectorStoreIndex
from pymongo import MongoClient
import os, faiss, gridfs

def embed_candidate(email, text):

    document = Document(text=text)
    embed_model = HuggingFaceEmbedding(model_name="hkunlp/instructor-xl")
    node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)
    Settings.embed_model = embed_model
    Settings.node_parser = node_parser

    # Create candidate directory if not exists
    user_index_dir = os.path.join("faiss_index", email)
    print("Extracting text from PDF:", user_index_dir)
    index_path = os.path.join(user_index_dir, "index.faiss")
    print("Index path:", index_path)
    os.makedirs(user_index_dir, exist_ok=True)

    # Load or create FAISS index
    if os.path.exists(index_path):
        print("Loading existing FAISS index from:", index_path)
        faiss_index = faiss.read_index(index_path)
    else:
        print("Creating new FAISS index for:", email)
        faiss_index = faiss.IndexFlatL2(768)  # 768 for instructor-xl

    # Build vector store
    print("Building vector store for user:", email)
    faiss_store = FaissVectorStore(faiss_index=faiss_index)

    # Build and persist the index for this user
    print("Creating VectorStoreIndex for user:", email)
    index = VectorStoreIndex.from_documents([document], vector_store=faiss_store)
    print("Persisting index for user:", email)
    index.storage_context.persist(persist_dir=user_index_dir)

    # Save the FAISS index file
    print("Saving FAISS index to:", index_path)
    faiss.write_index(faiss_index, index_path)

    return index

# Save the uploaded raw file in MongoDB using GridFS or as a binary field
def store_file_in_mongodb(file_path, email):
    print("Storing file in MongoDB:", file_path)
    mongo_uri = os.getenv("MONGO_URI", "mongodb://mongodb:27017/")
    print("MongoDB URI:", mongo_uri)
    client = MongoClient(mongo_uri)
    db = client["candidate_data"]
    fs = gridfs.GridFS(db)
    with open(file_path, "rb") as f:
        print("Reading file:", file_path)
        file_id = fs.put(f, filename=os.path.basename(file_path), email=email)
        print("File stored with ID:", file_id)
    return file_id