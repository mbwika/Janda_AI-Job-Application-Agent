# vector_store.py: Embeds & stores jobs using InstructorXL + FastEmbed.

# from fastembed.embedding import DefaultEmbedding
import logging
from fastembed import TextEmbedding
import json
import os

job_json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ey_jobs_us.json"))


# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JobVectorStore:
    def __init__(self):
        logger.info("Initializing JobVectorStore...")
        try:
            self.embedding_model = TextEmbedding(model_name="BAAI/bge-base-en")
            logger.info("Embedding model 'BAAI/bge-base-en' loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {e}")
            raise

        self.job_vectors = []

    def embed_jobs(self, job_json_path):
        logger.info(f"Embedding jobs from: {job_json_path}")

        if not os.path.exists(job_json_path):
            logger.error(f"Job JSON file not found: {job_json_path}")
            raise FileNotFoundError(f"File not found: {job_json_path}")

        try:
            with open(job_json_path, 'r') as f:
                jobs = json.load(f)
            logger.info(f"Loaded {len(jobs)} jobs.")
        except Exception as e:
            logger.error(f"Failed to load or parse job JSON: {e}")
            raise

        try:
            documents = [job['description'] for job in jobs]
            logger.info(f"Extracted {len(documents)} job descriptions.")

            vectors = list(self.embedding_model.embed(documents))
            logger.info("Job descriptions embedded successfully.")
        except Exception as e:
            logger.error(f"Error during embedding of job descriptions: {e}")
            raise

        try:
            self.job_vectors = [
                {"job": job, "vector": vec}
                for job, vec in zip(jobs, vectors)
            ]
            logger.info("Job vectors stored in memory.")
        except Exception as e:
            logger.error(f"Failed to store job vectors: {e}")
            raise

    def semantic_match(self, candidate_vector, top_k=5):
        logger.info("Performing semantic match...")

        def cosine_similarity(v1, v2):
            try:
                return sum(a * b for a, b in zip(v1, v2)) / (
                    sum(a * a for a in v1) ** 0.5 * sum(b * b for b in v2) ** 0.5
                )
            except Exception as e:
                logger.error(f"Error computing cosine similarity: {e}")
                return -1

        try:
            ranked = sorted(
                self.job_vectors,
                key=lambda jv: cosine_similarity(candidate_vector, jv["vector"]),
                reverse=True
            )
            logger.info(f"Top {top_k} matches computed.")
        except Exception as e:
            logger.error(f"Failed to perform semantic matching: {e}")
            raise

        return ranked[:top_k]


# from fastembed.embedding import DefaultEmbeddingModel, VectorStore

# class JobVectorStore:
#     def __init__(self):
#         self.model = DefaultEmbeddingModel(model_name="hkunlp/instructor-xl")
#         self.store = VectorStore(self.model)

#     def index_jobs(self, jobs: list):
#         for job in jobs:
#             self.store.add_document(job["id"], job["description"])

#     def query_similar_jobs(self, query: str, k: int = 5):
#         return self.store.search(query, k=k)