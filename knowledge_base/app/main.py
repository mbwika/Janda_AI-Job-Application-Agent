from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import os, shutil, json
from app.resume_parser import extract_text_from_pdf, extract_text_from_docx
from app.candidate_embedder import embed_candidate
from app.job_matcher import match_jobs

app = FastAPI()

@app.post("/upload-resume/")
async def upload_resume(file: UploadFile = File(...)):
    filename = file.filename or ""
    ext = os.path.splitext(filename)[-1].lower()
    if ext not in [".pdf", ".docx"]:
        return JSONResponse(status_code=400, content={"error": "Unsupported file type."})

    temp_path = f"temp{ext}"
    with open(temp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    if ext == ".pdf":
        text = extract_text_from_pdf(temp_path)
    else:
        text = extract_text_from_docx(temp_path)

    embed_candidate(text)
    os.remove(temp_path)

    return {"status": "Candidate profile stored successfully."}

@app.post("/match-jobs/")
async def match_job_list(file: UploadFile = File(...)):
    jobs = json.loads(await file.read())
    matched = match_jobs(jobs)
    return {"matched_jobs": matched}
