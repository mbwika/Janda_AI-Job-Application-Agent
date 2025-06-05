FROM python:3.10-slim

# Install system-level build tools and git
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    cmake \
    libpoppler-cpp-dev \
    tesseract-ocr \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN apt-get update && \
    apt-get install -y build-essential libpoppler-cpp-dev tesseract-ocr && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--limit-max-requests", "100"]

