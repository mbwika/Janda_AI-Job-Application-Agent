# job_agent.py
from crewai import Agent
# from langchain.llms import LlamaCpp
from langchain_community.llms import LlamaCpp
import os

llm = LlamaCpp(
    # Check if the model path is set in environment variables, otherwise use default
    model_path = os.getenv(
        "MODEL_PATH",
        os.path.abspath("models/mistral-7b-instruct-v0.2.Q4_K_M.gguf")
    ),
    # If the model path does not exist, download it from Hugging Face
    model_url = "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
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
