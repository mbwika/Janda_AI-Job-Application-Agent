import logging
import os
from crewai import Agent, Task, Crew
from app.rag.vector_store import JobVectorStore
from app.rag.profile_builder import ProfileBuilder
from fastembed import TextEmbedding

job_json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ey_jobs_us.json"))


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MatchAgentSetup:
    def __init__(self):
        logger.info("Initializing MatchAgentSetup...")
        self.vectorizer = TextEmbedding(model_name="BAAI/bge-base-en")
        logger.info("Vectorizer initialized.")

    def run(self, resume_text, job_json_path):
        logger.info("Starting agent run...")

        try:
            logger.info("Building profile from resume text...")
            profile_builder = ProfileBuilder()
            profile = profile_builder.build_profile(resume_text)
            logger.info("Profile built successfully.")
        except Exception as e:
            logger.error(f"Error in profile building: {e}")
            raise

        try:
            # After building the profile dict
            profile_dict = profile_builder.build_profile(resume_text)

            # Convert profile dict to a plain text string
            profile = "\n".join(f"{k}: {v}" for k, v in profile_dict.items())

            logger.info("Generating embedding for candidate profile...")
            candidate_embedding = list(self.vectorizer.embed([profile]))[0]
            logger.info("Embedding generated.")
        except Exception as e:
            logger.error(f"Error during embedding: {e}")
            raise

        try:
            logger.info(f"Loading job data from {job_json_path}...")
            vector_store = JobVectorStore()
            vector_store.embed_jobs(job_json_path)
            logger.info("Job data embedded.")

            logger.info("Performing semantic match...")
            top_jobs = vector_store.semantic_match(candidate_embedding)
            # Should return list of jobs where candidates meets 60% of the requirements
            logger.info(f"Top jobs retrieved: {len(top_jobs)} matches.")
        except Exception as e:
            logger.error(f"Error during semantic matching: {e}")
            raise

        logger.info("Agent run completed successfully.")
        return {
            "profile": profile,
            "top_jobs": [j["job"] for j in top_jobs]
        }