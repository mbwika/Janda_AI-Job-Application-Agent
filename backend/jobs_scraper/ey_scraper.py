# ey_scraper.py

from bs4 import BeautifulSoup
from pymongo import MongoClient
from urllib.parse import urljoin
import os, json, time, requests

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
}

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
base_url = "https://careers.ey.com"


from typing import Optional

def get_country_code(country: str) -> Optional[str]:
    return country_code_map.get(country.strip().lower())


def extract_job_links(soup):
    job_rows = soup.select("tr.data-row")
    return [urljoin(base_url, row.select_one("a.jobTitle-link")["href"])
            for row in job_rows if row.select_one("a.jobTitle-link")]


def find_next_page(soup):
    next_link = soup.select_one('a.pagination-link[aria-label="Next"]')
    return urljoin(base_url, next_link["href"]) if next_link and "href" in next_link.attrs else None


def extract_job_details(link):
    res = requests.get(link, headers=headers)
    job_soup = BeautifulSoup(res.text, "html.parser")

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
        "url": link,
    }


def scrape_ey_jobs(country: str) -> list:
    code = get_country_code(country)
    if not code:
        raise ValueError(f"Unsupported country: {country}")

    start_url = f"{base_url}/search/?createNewAlert=false&q=&locationsearch=&optionsFacetsDD_country={code}&optionsFacetsDD_customfield1="

    current_url = start_url
    all_job_links = []

    while current_url:
        res = requests.get(current_url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        all_job_links.extend(extract_job_links(soup))
        current_url = find_next_page(soup)
        time.sleep(1)

    all_job_links = list(set(all_job_links))
    all_jobs = []

    for link in all_job_links:
        try:
            all_jobs.append(extract_job_details(link))
        except Exception as e:
            print(f"Error scraping {link}: {e}")
        time.sleep(1)

    return all_jobs


def store_in_mongodb(jobs: list, collection_name="ey_jobs"):
    if not jobs:
        return

    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    client: MongoClient = MongoClient(mongo_uri, serverSelectionTimeoutMS=3000)
    db = client["job_data"]
    db[collection_name].insert_many(jobs)
    print(f"✅ Stored {len(jobs)} jobs in MongoDB collection '{collection_name}'.")


def main():
    country = input("🌍 Enter country (e.g., 'United States'): ")
    jobs = scrape_ey_jobs(country)
    if jobs:
        file_name = f"ey_jobs_{get_country_code(country)}.json"
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(jobs, f, indent=2, ensure_ascii=False)
        store_in_mongodb(jobs)
        print(f"✅ Saved {len(jobs)} jobs to {file_name}")
    else:
        print("⚠️ No jobs found.")


if __name__ == "__main__":
    main()
