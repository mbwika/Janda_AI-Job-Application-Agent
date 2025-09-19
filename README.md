# Janda_AI-Job-Search-Agent
Janda is a sophisticated, autonomous AI job search and application assistant — a highly practical use case that merges multi-agent orchestration, Retrieval-Augmented Generation (RAG) pipelines, LLM reasoning, resume/CV comparison, and web scraping/search APIs built using open-source and free tools. 

Key Components 

Component                                 : Functionality
1. Personal Knowledge Base                 1. Resume, project docs, LinkedIn profiles, and cover letters to learn the user’s expertise
2. Web Scraper                             2. Pulls jobs from websites based on filters like location, modality, and date
3. RAG Engine                              3. Matches jobs to user profiles and scores them by relevance
4. LLM Interface                           4. Generates a tailored resume, cover letter, and answers application questions
5. UI/UX Layer                             5. Lets the user review job matches and request assets

Summary: Tools & Technologies 

Module ==> Tech Stack (Free) 
1. Knowledge Base ==> LlamaIndex + FAISS + InstructorXL + MongoDB
2. Scraping ==> Playwright + BeautifulSoup 
3. LLM Inference ==> Mistral-7B via Hugging Face Transformers 
4. Agent Framework ==> CrewAI (multi-agent) + LangChain (tools & logic) 
5. Resume/Cover Letter Gen ==> LangChain + Prompt Templates + Knowledge Base 
6. RAG + QA ==> LlamaIndex (Production => Haystack) + Sentence Transformers 
7. UI ==> Streamlit / Gradio / FastAPI + React 

SETUP

1. For Docker setup, bake with `COMPOSE_BAKE=true docker compose up --build`


Run CI locally
----------------

To reproduce the GitHub Actions CI steps locally, use a Python 3.11/3.12 virtualenv and run the following commands:

```bash
# create a virtualenv (optional but recommended)
python -m venv .venv
source .venv/bin/activate

# upgrade pip and install dev deps
python -m pip install --upgrade pip
pip install -r requirements-dev.txt

# lint (flake8)
flake8 || true

# static types (mypy)
mypy || true

# run test suite
pytest -q

# security scan (bandit)
bandit -r backend/agents -n 5 || true
```

Notes:
- The `|| true` entries mirror the CI behavior where we run linters/type-checkers/bandit in best-effort mode; remove `|| true` to make these steps fail on errors.
- Use Python 3.11 or 3.12 to match the CI matrix.


  

  

 

