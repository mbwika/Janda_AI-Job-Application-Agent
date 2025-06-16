
# ey_scrapper.py
# This script scrapes job details from a specific job listing page on the EY careers website.
# only scrapes jobs on the first page: 25 jobs. needs to be modified to scrape all jobs with pagination.
# https://careers.ey.com/search/?locationsearch=&optionsFacetsDD_country=US&optionsFacetsDD_customfield1= 

from bs4 import BeautifulSoup
from pymongo import MongoClient
from urllib.parse import urljoin
import os, json, time, requests

# Mapping country names to country codes used in EY job URLs
country_code_map = {
    "united states": "US",
    "united kingdom": "GB",
    "canada": "CA",
    "germany": "DE",
    "india": "IN",
    "australia": "AU",
    "france": "FR",
    "japan": "JP",
    "china": "CN",
    "south africa": "ZA",
    # Add more as needed
}

def get_country_code():
    print("Available countries:")
    for name in sorted(country_code_map.keys()):
        print(f"  - {name.title()}")
    country = input("\n🌍 Enter country (e.g., 'United States'): ").strip().lower()
    code = country_code_map.get(country)
    if not code:
        print(f"❌ Country '{country}' is not supported.")
        exit(1)
    return code

def extract_job_links(soup):
    job_rows = soup.select('tr.data-row')
    links = []
    for row in job_rows:
        tag = row.select_one('a.jobTitle-link')
        if tag and tag.get('href'):
            links.append(urljoin(base_url, tag['href']))
    return links

def find_next_page(soup):
    next_link = soup.select_one('a.pagination-link[aria-label="Next"]')
    if next_link and 'href' in next_link.attrs:
        return urljoin(base_url, next_link['href'])
    return None

def extract_job_details(link):
    response = requests.get(link, headers=headers)
    job_soup = BeautifulSoup(response.text, 'html.parser')

    def extract(selector):
        el = job_soup.select_one(selector)
        return el.get_text(strip=True) if el else None

    return {
        "title": extract('span[data-careersite-propertyid="title"]'),
        "location": extract('span[data-careersite-propertyid="city"]'),
        "other_locations": extract('span[data-careersite-propertyid="customfield3"]'),
        "salary": extract('div.custom__view__job-page__salary span[lang="en-US"]'),
        "posted_date": extract('span[data-careersite-propertyid="date"]'),
        "description": extract('span[data-careersite-propertyid="description"]'),
        "url": link
    }

# Setup
base_url = "https://careers.ey.com"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
country_code = get_country_code()
start_url = f"{base_url}/search/?createNewAlert=false&q=&locationsearch=&optionsFacetsDD_country={country_code}&optionsFacetsDD_customfield1="

# Crawl all job URLs with pagination
current_url = start_url
all_job_links = []

print(f"\n🔄 Collecting jobs for country code: {country_code}")
while current_url:
    print(f"Fetching: {current_url}")
    res = requests.get(current_url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    all_job_links.extend(extract_job_links(soup))
    current_url = find_next_page(soup)
    time.sleep(1)

all_job_links = list(set(all_job_links))
print(f"\n🧭 Found {len(all_job_links)} job links.")

# Scrape job details
all_jobs = []
for i, link in enumerate(all_job_links, 1):
    print(f"[{i}/{len(all_job_links)}] Scraping {link}")
    try:
        job = extract_job_details(link)
        all_jobs.append(job)
    except Exception as e:
        print(f"⚠️ Error scraping {link}: {e}")
    time.sleep(1)

# Save  in JSON file
file_name = f"ey_jobs_{country_code.lower()}.json"
with open(file_name, "w", encoding="utf-8") as f:
    json.dump(all_jobs, f, indent=2, ensure_ascii=False)

print(f"\n✅ Done. Saved {len(all_jobs)} jobs to {file_name}")

# Store results in MongoDB/BSON file
mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
try:
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=3000)
    client.server_info()  # Force connection on a request as the
    db = client["job_data"]
    with open(file_name, "r", encoding="utf-8") as f:
        data = json.load(f)
        if data:
            db.ey_jobs.insert_many(data)
            print(f"✅ Stored {len(data)} jobs in MongoDB collection 'ey_jobs'.")
        else:
            print("⚠️ No job data to store in MongoDB.")
except Exception as e:
    print(f"❌ Could not connect to MongoDB or store data: {e}")