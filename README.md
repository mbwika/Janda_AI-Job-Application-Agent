# Janda_AI-Job-Search-Agent
Janda is a sophisticated, autonomous AI job search and application assistant — a highly practical use case that merges multi-agent orchestration, Retrieval-Augmented Generation (RAG) pipelines, LLM reasoning, resume/CV comparison, and web scraping/search APIs built using open-source and free tools. 

🚧 Repo Structure 

ai-job-search-agent/ 
│ 

├── ingest/                        # Resume, LinkedIn, cover letter loaders 

├── embeddings/              # Embedding + FAISS vector store setup 

├── jobs/                           # Scrapers for LinkedIn, Indeed, etc. 

├── scoring/                      # Matching engine and suitability logic 

├── generation/                # Resume & cover letter templates + LLM prompts 

├── qa/                             # App question answerer 

├── ui/                              # Streamlit, React, or Gradio frontend 

├── config.yaml               # Job search filters and preferences 

├── main.py                     # Entry point to pipeline 

└── requirements.txt

Key Components 

Component                                 : Functionality
1. Personal Knowledge Base                 1. Resume, project docs, LinkedIn profiles, and cover letters to learn the user’s expertise
2. Web Scraper / Job API Crawler           2. Pulls jobs from websites based on filters like location, modality, and date
3. RAG Engine                              3. Matches jobs to user profiles and scores them by relevance
4. LLM Interface                           4. Generates a tailored resume, cover letter, and answers application questions
5. UI/UX Layer (Optional)                  5. Lets the user review job matches and request assets

Summary: Tools & Technologies 

Module ==> Tech Stack (Free) 
1. Knowledge Base ==> LlamaIndex + FAISS + InstructorXL or BGE
2. Scraping ==> Playwright or Selenium + BeautifulSoup 
3. LLM Inference ==> Mistral-7B via Hugging Face Transformers or LM Studio 
4. Agent Framework ==> CrewAI (multi-agent) + LangChain (tools & logic) 
5. Resume/Cover Letter Gen ==> LangChain + Prompt Templates + ResumeData 
6. RAG + QA ==> Haystack + Sentence Transformers 
7. UI ==> Streamlit / Gradio / FastAPI + React 


  

  

 

