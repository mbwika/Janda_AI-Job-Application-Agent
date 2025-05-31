# Dockerfile
FROM python:3.11
WORKDIR /app
COPY . .

# Add app root to PYTHONPATH
ENV PYTHONPATH=/app

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]