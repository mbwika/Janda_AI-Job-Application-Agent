

# job_matcher.py
# from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.embeddings.fastembed import FastEmbedEmbedding
from llama_index.core import Settings
from llama_index.llms.llama_cpp import LlamaCPP
from llama_index.core import StorageContext, load_index_from_storage
import requests
import os

def match_jobs(email: str, jobs):
    # Settings.embed_model = HuggingFaceEmbedding(model_name="hkunlp/instructor-xl")
    Settings.embed_model = FastEmbedEmbedding(model_name="BAAI/bge-base-en-v1.5")
    user_dir = f"faiss_index/{email}"

    model_path = os.getenv(
    "MODEL_PATH",
    os.path.abspath("models/mistral-7b-instruct-v0.2.Q4_K_M.gguf")
     )
    model_url = "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
    
    if not os.path.exists(os.path.join(user_dir, "default__vector_store.json")):
        raise RuntimeError(f"Vector store not found for {email}. Please upload resume first.")

    # load vector store & index from directory, not file
    storage_context = StorageContext.from_defaults(persist_dir=user_dir)
    index = load_index_from_storage(storage_context)

    # Call function to ensure the model file exists
    ensure_model(model_path, model_url)
    Settings.llm = LlamaCPP(
        model_path=model_path,
        temperature=0.1,
        max_new_tokens=512,
        context_window=2048,
    )

    query_engine = index.as_query_engine(similarity_top_k=5)

    matches = []
    for job in jobs:
        job_text = f"{job.get('title', 'No Title')} at {job.get('company', 'EY')}. Requirements: {job.get('requirements', 'Not specified')}"
        response = query_engine.query(job_text)
        score = response.source_nodes[0].score if response.source_nodes else 0
        score = score if score is not None else 0
        score_percent = round(score * 100, 2)
        if score_percent >= 70:
            matches.append({**job, "match_score": score_percent})

    matches.sort(key=lambda x: x["match_score"], reverse=True)
    
    return matches


def ensure_model(model_path: str, model_url: str):
    if not os.path.exists(model_path):
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        print(f"Downloading model from {model_url} ...")
        response = requests.get(model_url, stream=True)
        with open(model_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("Model download complete.")



