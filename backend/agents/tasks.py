# agents/tasks.py

from crewai import Task
from .base_agents import (
    UserInteractionAgent,
    JobScraperAgent,
    UserProfileAgent,
    MatcherAgent,
    ResumeGeneratorAgent,
    JobApplicationAgent
)

# Task 1: Upload user documents and populate knowledge base
ResumeUploadTask = Task(
    description=(
        "Engage with the user to upload their resume or profile documents. "
        "Trigger the RAG pipeline by executing the script that ingests the uploaded data, "
        "stores it in MongoDB (raw files), and updates the FAISS vector index. "
        "Wait for confirmation that ingestion is complete and inform the team."
    ),
    expected_output="Confirmation that user's knowledge base is populated.",
    agent=UserInteractionAgent
)

# Task 2: Trigger job scraping script and wait for JSON output
JobScrapingTask = Task(
    description=(
        "Run the Python scripts responsible for scraping job boards like LinkedIn or Glassdoor. "
        "Execute these scripts from the filesystem and return a confirmation when job listings "
        "have been stored in JSON format. Provide file paths to the output."
    ),
    expected_output="Paths to the scraped job JSON files.",
    agent=JobScraperAgent
)

# Task 3: Build user profile from MongoDB/FAISS knowledge base
ProfileBuildingTask = Task(
    description=(
        "Analyze the user data in the knowledge base and build a structured user profile. "
        "Use the embedded vectors and metadata from MongoDB to extract skills, experience, and preferences. "
        "Identify user by their email address and output a structured JSON profile."
    ),
    expected_output="Structured user profile in JSON format.",
    agent=UserProfileAgent
)

# Task 4: Match profile to jobs with 70%+ score
MatchingTask = Task(
    description=(
        "Using the previously generated user profile, run the matching engine to compare "
        "the profile against the scraped job listings. Use cosine similarity or semantic scoring. "
        "Only return jobs that match at least 70% of the user’s qualifications and preferences."
    ),
    expected_output="List of matched jobs (70%+ match score).",
    agent=MatcherAgent
)

# Task 5: Generate tailored resumes and cover letters
ResumeTailoringTask = Task(
    description=(
        "For each matched job, generate a tailored resume and a persuasive cover letter. "
        "Use the user profile and the job description to personalize the content. "
        "Ensure formatting and tone are appropriate for professional applications."
    ),
    expected_output="Tailored resume and cover letter per job, in Markdown or PDF-ready text.",
    agent=ResumeGeneratorAgent
)

# Task 6: Automate the job application process
JobApplicationTask = Task(
    description=(
        "Visit the application link for each selected job. "
        "Fill out required fields using user data and resume. "
        "Answer application questions intelligently based on context. "
        "Submit the job application and return a confirmation or screenshot/log."
    ),
    expected_output="Application submission confirmation per job.",
    agent=JobApplicationAgent
)
