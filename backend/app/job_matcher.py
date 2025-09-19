"""Job matching utilities.

This module provides `match_jobs` which loads a FAISS-backed index for a
user (persisted under `faiss_index/<email>`) and uses an LLM-backed query
engine to score job postings against the user's resume.

Important environment variables used here:
- `MODEL_PATH` - path to local LLM model file (default: `models/mistral-...gguf`).
- `MODEL_URL` - where to download the model from if auto-download is enabled.
- `MODEL_AUTO_DOWNLOAD` - set to `false` to avoid downloading models during import/tests.
- `MODEL_DOWNLOAD_PROGRESS` - enable progress logging for model download.
- `MODEL_SHA256` - optional checksum for model verification.

The `match_jobs` function is written to be testable: it checks for a small
file (`default__vector_store.json`) in the user's FAISS directory before
attempting to load the index. Tests can set `MODEL_AUTO_DOWNLOAD=false` and
monkeypatch LlamaCPP/load_index_from_storage to avoid loading real models.
"""

from llama_index.embeddings.fastembed import FastEmbedEmbedding
from llama_index.core import Settings
from llama_index.llms.llama_cpp import LlamaCPP
from llama_index.core import StorageContext, load_index_from_storage
from pymongo import MongoClient
import gridfs
import os
import logging
from backend.utils.download import download_model
from backend.logging_config import configure_logging  # ensure logging configured for modules

logger = logging.getLogger(__name__)


def get_user_raw_file(email: str):
    """Fetch raw (binary) uploaded file for the user from MongoDB/GridFS.

    Raises RuntimeError if the file isn't present.
    """
    logger.debug("Fetching raw file for user: %s", email)
    mongo_uri = os.getenv("MONGO_URI", "mongodb://mongodb:27017/")
    logger.debug("MongoDB URI: %s", mongo_uri)
    client = MongoClient(mongo_uri)
    db = client.get("candidate_data") if hasattr(client, 'get') else client["candidate_data"]
    fs = gridfs.GridFS(db)
    logger.debug("Searching for file in MongoDB for email: %s", email)
    file_doc = fs.find_one({"email": email})
    if file_doc:
        logger.info("File found for %s, returning content.", email)
        return file_doc.read()
    else:
        raise RuntimeError(f"Files for {email} not found. Please upload resume first.")


def match_jobs(email: str, jobs):
    """Match a list of job postings to a user's stored resume/index.

    The function returns a dict with keys `matches` (list) and `raw_file`
    (binary content) for downstream use. It raises RuntimeError on missing
    inputs (e.g. missing FAISS vector store directory).
    """

    logger.info("Matching jobs for user: %s", email)
    Settings.embed_model = FastEmbedEmbedding(model_name="BAAI/bge-base-en-v1.5")
    logger.debug("Using FastEmbedEmbedding for job matching.")
    user_dir = f"faiss_index/{email}"

    logger.debug("User directory for index: %s", user_dir)
    model_path = os.getenv(
        "MODEL_PATH",
        os.path.abspath("models/mistral-7b-instruct-v0.2.Q4_K_M.gguf")
    )
    model_url = os.getenv(
        "MODEL_URL",
        "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
    )

    # Ensure vector store exists
    if not os.path.exists(os.path.join(user_dir, "default__vector_store.json")):
        raise RuntimeError(f"Vector store not found for {email}. Please upload resume first.")

    # load vector store & index from directory
    logger.debug("Loading index from storage context for user: %s", email)
    storage_context = StorageContext.from_defaults(persist_dir=user_dir)
    logger.debug("Storage context created, loading index...")
    index = load_index_from_storage(storage_context)

    # Download model if configured to
    model_auto_download = os.getenv("MODEL_AUTO_DOWNLOAD", "true").lower() not in ("0", "false", "no")
    if model_auto_download:
        try:
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            download_model(
                model_url,
                model_path,
                model_sha256=os.getenv("MODEL_SHA256"),
                progress=os.getenv("MODEL_DOWNLOAD_PROGRESS", "false").lower() in ("1", "true", "yes"),
            )
        except Exception:
            logger.exception("Failed to ensure model is present at %s", model_path)
            raise

    logger.info("Initializing LlamaCPP with model at %s", model_path)
    Settings.llm = LlamaCPP(
        model_path=model_path,
        temperature=0.1,
        max_new_tokens=512,
        context_window=2048,
    )

    logger.debug("LlamaCPP model set for querying.")
    query_engine = index.as_query_engine(similarity_top_k=5)

    # Fetch raw file from MongoDB
    logger.debug("Fetching raw file for user: %s", email)
    raw_file = get_user_raw_file(email)

    matches = []
    logger.info("Matching jobs against %d job postings.", len(jobs))
    for job in jobs:
        job_text = f"{job.get('title', 'No Title')} at {job.get('company', 'EY')}. Requirements: {job.get('requirements', 'Not specified')}"
        response = query_engine.query(job_text)
        logger.debug("Queried for job: %s", job.get('title', 'No Title'))
        score = response.source_nodes[0].score if response.source_nodes else 0
        score = score if score is not None else 0
        score_percent = round(score * 100, 2)
        if score_percent >= 70:
            logger.info("Job %s matched with score: %s%%", job.get('title', 'No Title'), score_percent)
            matches.append({**job, "match_score": score_percent})

    matches.sort(key=lambda x: x["match_score"], reverse=True)

    logger.info("Found %d matching jobs for user: %s", len(matches), email)
    return {
        "matches": matches,
        "raw_file": raw_file,  # This is the binary content of the user's file
    }