# job_agent.py
from crewai import Agent
# from langchain.llms import LlamaCpp
from langchain_community.llms import LlamaCpp
import os
import requests

MODEL_PATH = os.getenv(
    "MODEL_PATH",
    os.path.abspath("models/mistral-7b-instruct-v0.2.Q4_K_M.gguf")
)
MODEL_URL = "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf"

# Ensure model directory exists
os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

# Download model if not present
if not os.path.exists(MODEL_PATH):
    print(f"Model file not found at {MODEL_PATH}. Downloading from {MODEL_URL}...")
    response = requests.get(MODEL_URL, stream=True)
    if response.status_code == 200:
        with open(MODEL_PATH, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"Model downloaded to {MODEL_PATH}.")
    else:
        raise RuntimeError(f"Failed to download model from {MODEL_URL}. Status code: {response.status_code}")

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
