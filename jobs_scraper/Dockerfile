# where in docker are files from jobs_scraper copied?

FROM python:3.11-slim
WORKDIR /app
COPY . /jobs_scraper
RUN pip install --no-cache-dir -r /jobs_scraper/requirements.txt
CMD ["python", "ey_scraper.py", "motion-recruitment_scraper.py"]