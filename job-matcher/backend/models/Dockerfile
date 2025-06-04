

# rag-job-matcher/backend/models/Dockerfile

FROM ghcr.io/ggerganov/llama.cpp:server-cuda

RUN apt-get update && apt-get install -y python3 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Reference the JSON file from the root-level context (since docker-compose context is ".")
COPY backend/app/ey_jobs_us.json ./ey_jobs_us.json

ENV MODEL=/models/mistral-7b-instruct-v0.2.Q4_K_M.gguf

CMD ["--model", "/models/mistral-7b-instruct-v0.2.Q4_K_M.gguf", "--host", "0.0.0.0", "--port", "8000"]
