FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN apt-get update && \
    apt-get install -y build-essential libpoppler-cpp-dev tesseract-ocr && \
    pip install --upgrade pip && \
    pip install fastapi uvicorn pdfplumber python-docx llama-index==0.10.32 faiss-cpu InstructorEmbedding huggingface-hub && \
    pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
