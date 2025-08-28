# job_matcher.py

from llama_index.embeddings.fastembed import FastEmbedEmbedding
from llama_index.core import Settings
from llama_index.llms.llama_cpp import LlamaCPP
from llama_index.core import StorageContext, load_index_from_storage
from pymongo import MongoClient
import gridfs
import os, requests, json

def get_user_raw_file(email):
    print(f"Fetching raw file for user: {email}")
    mongo_uri = os.getenv("MONGO_URI", "mongodb://mongodb:27017/")
    print("MongoDB URI:", mongo_uri)
    client = MongoClient(mongo_uri)
    db = client["candidate_data"]
    fs = gridfs.GridFS(db)
    print("Searching for file in MongoDB for email:", email)
    file_doc = fs.find_one({"email": email})
    if file_doc:
        print(f"File found for {email}, returning content.")
        return file_doc.read()
    else:
        raise RuntimeError(f"Files for {email} not found. Please upload resume first.")
    # return None

def match_jobs(email: str, jobs):
    print(f"Matching jobs for user: {email}")
    Settings.embed_model = FastEmbedEmbedding(model_name="BAAI/bge-base-en-v1.5")
    print("Using FastEmbedEmbedding for job matching.")
    user_dir = f"faiss_index/{email}"

    print(f"User directory for index: {user_dir}")
    model_path = os.getenv(
        "MODEL_PATH",
        os.path.abspath("models/mistral-7b-instruct-v0.2.Q4_K_M.gguf")
    )
    model_url = "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
    
    if not os.path.exists(os.path.join(user_dir, "default__vector_store.json")):
     raise RuntimeError(f"Vector store not found for {email}. Please upload resume first.")

    # load vector store & index from directory, not file
    print(f"Loading index from storage context for user: {email}")
    storage_context = StorageContext.from_defaults(persist_dir=user_dir)
    print("Storage context created, loading index...")
    index = load_index_from_storage(storage_context)

    # Call function to ensure the model file exists
    print(f"Ensuring model at {model_path} exists...")
    ensure_model(model_path, model_url)
    Settings.llm = LlamaCPP(
        model_path=model_path,
        temperature=0.1,
        max_new_tokens=512,
        context_window=2048,
    )

    print("LlamaCPP model set for querying.")
    query_engine = index.as_query_engine(similarity_top_k=5)

    # Fetch raw file from MongoDB
    print(f"Fetching raw file for user: {email}")
    raw_file = get_user_raw_file(email)


    matches = []
    print(f"Matching jobs against {len(jobs)} job postings.")
    for job in jobs:
        job_text = f"{job.get('title', 'No Title')} at {job.get('company', 'EY')}. Requirements: {job.get('requirements', 'Not specified')}"
        response = query_engine.query(job_text)
        print(f"Querying for job: {job.get('title', 'No Title')}")
        score = response.source_nodes[0].score if response.source_nodes else 0
        score = score if score is not None else 0
        score_percent = round(score * 100, 2)
        if score_percent >= 70:
            print(f"Job {job.get('title', 'No Title')} matched with score: {score_percent}%")
            matches.append({**job, "match_score": score_percent})

    matches.sort(key=lambda x: x["match_score"], reverse=True)
    
    # Combine FAISS vector results and raw file for downstream use
    print(f"Found {len(matches)} matching jobs for user: {email}")
    return {
        "matches": matches,
        "raw_file": raw_file  # This is the binary content of the user's file
    }


def ensure_model(model_path: str, model_url: str):
    if not os.path.exists(model_path):
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        print(f"Downloading model from {model_url} ...")
        response = requests.get(model_url, stream=True)
        with open(model_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("Model download complete.")