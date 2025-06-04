
# ey_scrapper.py
# This script scrapes job details from a specific job listing page on the EY careers website.

# https://careers.ey.com/search/?locationsearch=&optionsFacetsDD_country=US&optionsFacetsDD_customfield1= 

from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import json
import time

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

# Save results
file_name = f"ey_jobs_{country_code.lower()}.json"
with open(file_name, "w", encoding="utf-8") as f:
    json.dump(all_jobs, f, indent=2, ensure_ascii=False)

print(f"\n✅ Done. Saved {len(all_jobs)} jobs to {file_name}")


# from bs4 import BeautifulSoup
# import requests
# from urllib.parse import urljoin

# # base_url = "https://careers.ey.com/search/?locationsearch=&optionsFacetsDD_country=&optionsFacetsDD_customfield1="
# location_us_url = "https://careers.ey.com/search/?createNewAlert=false&q=&locationsearch=&optionsFacetsDD_country=US&optionsFacetsDD_customfield1="
# url_trim = "https://careers.ey.com/"
# response = requests.get(location_us_url)
# soup = BeautifulSoup(response.text, 'html.parser')

# # Select the first <tr class="data-row"> as the row to extract job info from
# row = soup.select_one('tr.data-row')
# job_link_tag = row.select_one('a.jobTitle-link') if row else None
# job_location_tag = row.select_one('td.colLocation .jobLocation') if row else None

# # Find all job rows
# job_rows = soup.select('tr.data-row')

# # Collect job details from each row
# all_jobs = []
# for row in job_rows:
#     job_link_tag = row.select_one('a.jobTitle-link')
    
#     job_details = {
#         "title": job_link_tag.get_text(strip=True) if job_link_tag else None,
#         "url": urljoin(url_trim, job_link_tag['href']) if job_link_tag else None
#     }

#     if job_details["title"] and job_details["url"]:
#         all_jobs.append(job_details)

# # Output all collected jobs
# for job in all_jobs:
#     print(job)

# job_details = {
#     "title": job_link_tag.get_text(strip=True) if job_link_tag else None,
#     # "company": soup.select_one('div.company').get_text(strip=True) if soup.select_one('div.company') else None,
#     # "location": soup.select_one('div.location').get_text(strip=True) if soup.select_one('div.location') else None,
#     # "work_mode": soup.select_one('div.workMode').get_text(strip=True) if soup.select_one('div.workMode') else None,
#     # "posted_date": soup.select_one('div.postedDate').get_text(strip=True) if soup.select_one('div.postedDate') else None,
#     # "description": soup.select_one('div.jobDescription').get_text(strip=True) if soup.select_one('div.jobDescription') else None,
#     "url": urljoin(url_trim, job_link_tag['href']) if job_link_tag else None
# }

# print(job_details)
