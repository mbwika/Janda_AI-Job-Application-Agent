
# job_matcher.py
from llama_index.core import StorageContext
# from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings
from llama_index.llms.llama_cpp import LlamaCPP
from llama_index.core import StorageContext, load_index_from_storage
import os

def match_jobs(jobs):
    Settings.embed_model = HuggingFaceEmbedding(model_name="hkunlp/instructor-xl")
    base_dir = os.path.dirname(__file__)
    model_path = os.path.abspath(os.path.join(base_dir, "../../job-matcher/models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"))
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    FAISS_INDEX_PATH = os.path.join(BASE_DIR, "faiss_index", "index.faiss")
    persist_path = "faiss_index/"
    if not os.path.exists(os.path.join(persist_path, "default__vector_store.json")):
        raise RuntimeError("Vector store not found. Please run the index builder first.")
    # print("Files in faiss_index:", os.listdir(FAISS_INDEX_PATH))
    
    # vector_store = FaissVectorStore.from_persist_path(persist_path=FAISS_INDEX_PATH)
    storage_context = StorageContext.from_defaults(persist_dir="faiss_index")
    index = load_index_from_storage(storage_context)
    Settings.llm = LlamaCPP(
    model_path=model_path,
    temperature=0.1,
    max_new_tokens=512,
    context_window=2048
)
    query_engine = index.as_query_engine(similarity_top_k=5)

    matches = []
    for job in jobs:
        # job_text = f"{job['title']} at {job['company']}. Requirements: {job['requirements']}"
        job_text = f"{job.get('title', 'No Title')} at {job.get('company', 'EY')}. Requirements: {job.get('requirements', 'Not specified')}"
        response = query_engine.query(job_text)
        score = response.source_nodes[0].score if response.source_nodes else 0
        score = score if score is not None else 0
        score_percent = round(score * 100, 2)

        if score_percent >= 70:
            matches.append({**job, "match_score": score_percent})
            print(f"\n\n") 

    # Sort by match_score in descending order   
    matches.sort(key=lambda x: x["match_score"], reverse=True)

    return matches
