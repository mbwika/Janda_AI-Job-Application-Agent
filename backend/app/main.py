# main.py

from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse
import os
import shutil
import json

from app.resume_parser import extract_text_from_pdf, extract_text_from_docx
from app.candidate_embedder import embed_candidate, store_file_in_mongodb
from app.job_matcher import match_jobs
from app.user_profile_utils import check_user_profile
from fastapi.middleware.cors import CORSMiddleware
from agents.orchestrator import run_agents_for_user

from crewai import Crew
from agents.tasks import (
    ResumeUploadTask, JobScrapingTask, ProfileBuildingTask,
    MatchingTask, ResumeTailoringTask, JobApplicationTask
)

# Optional: scraping tools
# main.py
from jobs_scraper.ey_scraper import scrape_ey_jobs, store_in_mongodb
from jobs_scraper.motion_scraper import scrape_motion_jobs, store_in_mongodb


from app.user_profile_utils import check_user_profile

app = FastAPI()

# Allow CORS for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://janda-frontend:8501"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/upload-resume/")
async def upload_resume(email: str = Form(...), file: UploadFile = File(...)):
    filename = file.filename or ""
    ext = os.path.splitext(filename)[-1].lower()
    if ext not in [".pdf", ".docx"]:
        return JSONResponse(status_code=400, content={"error": "Unsupported file type."})

    temp_path = f"temp{ext}"
    with open(temp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        # Store raw file in MongoDB
        store_file_in_mongodb(temp_path, email)

        # Extract text & embed
        text = extract_text_from_pdf(temp_path) if ext == ".pdf" else extract_text_from_docx(temp_path)
        embed_candidate(email=email, text=text)
    finally:
        os.remove(temp_path)

    return {"status": f"Resume stored and processed for {email}"}


@app.post("/match-jobs/")
async def match_job_list(email: str = Form(...), file: UploadFile = File(...)):
    jobs = json.loads(await file.read())
    matched = match_jobs(email=email, jobs=jobs)
    return {"matched_jobs": matched}


@app.post("/run-multiagent/")
async def run_full_pipeline(background_tasks: BackgroundTasks):
    """
    Triggers full CrewAI orchestration in background (non-blocking).
    """
    def run_crew_tasks():
        agent_list = [
            ResumeUploadTask.agent,
            JobScrapingTask.agent,
            ProfileBuildingTask.agent,
            MatchingTask.agent,
            ResumeTailoringTask.agent,
            JobApplicationTask.agent,
        ]
        agent_list = [agent for agent in agent_list if agent is not None]
        crew = Crew(
            agents=agent_list,
            tasks=[
                ResumeUploadTask,
                JobScrapingTask,
                ProfileBuildingTask,
                MatchingTask,
                ResumeTailoringTask,
                JobApplicationTask,
            ],
            verbose=True
        )
        crew.kickoff()

    background_tasks.add_task(run_crew_tasks)
    return {"status": "Multi-agent system started in background"}

@app.post("/run-multiagent/")
async def run_multiagent(email: str = Form(...)):
    try:
        # Trigger CrewAI or LangChain flow using the email
        
        run_agents_for_user(email)
        return {"status": "success", "message": "Agents started."}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/")
async def root():
    return {"message": "AI Job Assistant is running"}

@app.post("/check-profile/")
async def check_profile(email: str = Form(...)):
    try:
        exists = check_user_profile(email)
        if exists:
            return {"status": "exists", "message": "✅ Profile found. You may proceed to job search."}
        else:
            return {"status": "new", "message": "📄 No profile found. Please upload your resume to begin."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/scrape-ey-jobs/")
async def scrape_ey(country: str = Form(...)):
    try:
        jobs = scrape_ey_jobs(country)
        store_in_mongodb(jobs)
        return {"status": "success", "jobs_scraped": len(jobs)}
    except ValueError as ve:
        return {"status": "error", "message": str(ve)}
    except Exception as e:
        return {"status": "error", "message": f"Failed to scrape: {e}"}

@app.post("/scrape-motion-jobs/")
async def scrape_motion():
    try:
        jobs = await scrape_motion_jobs()
        store_in_mongodb(jobs)
        return {"status": "success", "jobs_scraped": len(jobs)}
    except Exception as e:
        return {"status": "error", "message": str(e)}
