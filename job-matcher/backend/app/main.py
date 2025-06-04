# app/main.py FastAPI endpoint to trigger the match process from an uploaded resume.


from fastapi import FastAPI, UploadFile, File, HTTPException
from app.agents.crew_setup import MatchAgentSetup
import pdfplumber
import io
import os

# Resolve path to ey_jobs_us.json relative to this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
job_json_path = os.path.join(BASE_DIR, "ey_jobs_us.json")  # if code is in app 

app = FastAPI()

@app.post("/match")
async def match_resume(resume: UploadFile = File(...)):
    print("Endpoint hit: /match")
    print(f"Received file: {resume.filename} ({resume.content_type})")

    if resume.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Please upload a valid PDF file.")

    file_bytes = await resume.read()
    print(f"Read {len(file_bytes)} bytes from file")

    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
    except Exception as e:
        print("Error extracting text from PDF:", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to extract text from PDF: {str(e)}")

    if not text.strip():
        raise HTTPException(status_code=400, detail="No text could be extracted from the PDF.")

    print("Text extracted successfully")
    
    agent_system = MatchAgentSetup()
    result = agent_system.run(text, job_json_path)

    print("Agent result:", result)

    return result
