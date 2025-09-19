"""Agent definitions and LLM wiring.

This module defines the higher-level Agent objects used by the application and
wires them to a shared `llm` instance. The module intentionally keeps
initialization simple: the LLM is created at import time from a local model
path. For testability, automatic model download can be disabled via
`MODEL_AUTO_DOWNLOAD=false` and the `LlamaCpp` symbol can be monkeypatched in
tests to avoid loading a real model.
"""
from crewai import Agent
# from langchain.llms import LlamaCpp
from langchain_community.llms import LlamaCpp
import os
import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException
from urllib3.util.retry import Retry
import hashlib
import tempfile
import sys
import time
import logging

MODEL_PATH = os.getenv(
    "MODEL_PATH",
    os.path.abspath("models/mistral-7b-instruct-v0.2.Q4_K_M.gguf")
)
MODEL_URL = "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf"

from backend.logging_config import configure_logging  # ensures logging is configured
from backend.utils.download import download_model

# Ensure model directory exists
os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

logger = logging.getLogger(__name__)

# Auto-download guard: allow disabling automatic download during imports/tests
# Default is enabled; set MODEL_AUTO_DOWNLOAD=false to prevent auto-download.
# This makes tests faster and avoids network I/O at import time.
MODEL_AUTO = os.getenv("MODEL_AUTO_DOWNLOAD", "true").lower() in ("1", "true", "yes")
if MODEL_AUTO and not os.path.exists(MODEL_PATH):
    # Attempt to download model using the shared download util. Any exception
    # will propagate so the host can see errors during startup.
    download_model(
        MODEL_URL,
        MODEL_PATH,
        model_sha256=os.getenv("MODEL_SHA256"),
        timeout=(10, 60),
        total_retries=5,
        backoff_factor=1,
        progress=os.getenv("MODEL_DOWNLOAD_PROGRESS", "false").lower() in ("1", "true", "yes"),
    )

# Instantiate LLM only when model is present (or assumed to be present).
# Note: if you want to avoid instantiating a real LLM in unit tests, set
# MODEL_AUTO_DOWNLOAD=false and monkeypatch `LlamaCpp` to a dummy class before
# importing this module.
llm = LlamaCpp(
    model_path=MODEL_PATH,
    temperature=0.2,
    max_tokens=1024,
    n_ctx=4096,
    n_gpu_layers=35,
    verbose=True
)

UserInteractionAgent = Agent(
    role="User Interaction Assistant",
    goal="Guide user to upload resumes and trigger knowledge ingestion",
    backstory="You help the user upload resumes and initialize the RAG pipeline.",
    verbose=True,
    llm=llm
)

JobScraperAgent = Agent(
    role="Job Scraping Agent",
    goal="Run job scraping scripts and ensure JSON job data is ready",
    backstory="You automate job scraping and prepare structured output.",
    verbose=True,
    llm=llm
)

UserProfileAgent = Agent(
    role="Profile Builder",
    goal="Construct structured user profile from RAG knowledge base",
    backstory="You extract data from FAISS+MongoDB to create a complete profile.",
    verbose=True,
    llm=llm
)

MatcherAgent = Agent(
    role="Job Matcher",
    goal="Match user profiles to jobs and filter matches above 70%",
    backstory="You match user strengths to job requirements using semantic similarity.",
    verbose=True,
    llm=llm
)

ResumeGeneratorAgent = Agent(
    role="Resume Tailor",
    goal="Generate tailored resume and cover letter using job context",
    backstory="You use user history and job description to craft persuasive application documents.",
    verbose=True,
    llm=llm
)

JobApplicationAgent = Agent(
    role="Application Submitter",
    goal="Auto-fill and submit job application forms based on job link",
    backstory="You help automate the application process by filling out forms and submitting them.",
    verbose=True,
    llm=llm
)
