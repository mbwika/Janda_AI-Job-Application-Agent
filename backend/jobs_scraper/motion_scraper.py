# motion_scraper.py

import os, json, asyncio
from playwright.async_api import async_playwright
from pymongo import MongoClient

BASE_URL = "https://motionrecruitment.com"
SEARCH_URL = f"{BASE_URL}/tech-jobs"


async def scrape_motion_jobs():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(SEARCH_URL, timeout=120_000)

        await page.wait_for_selector("ul.JobsList_module_list")
        job_elements = await page.query_selector_all("li.JobItem_module_jobItem")

        jobs = []

        for job_element in job_elements:
            title_el = await job_element.query_selector("h2.JobItem_module_title")
            title = await title_el.inner_text() if title_el else "N/A"

            link_el = await job_element.query_selector("a")
            relative_url = await link_el.get_attribute("href") if link_el else "#"
            job_url = BASE_URL + (relative_url or "")

            location_el = await job_element.query_selector("div.JobItem_module_jobDetailsSection > p")
            location = await location_el.inner_text() if location_el else "N/A"

            wrapper_el = await job_element.query_selector("div.JobItem_module_jobDetailsWrapper > b")
            workplace = await wrapper_el.inner_text() if wrapper_el else "N/A"

            job_type_els = await job_element.query_selector_all("p.JobDetailsItem_module_jobDetailsText")
            job_type = await job_type_els[0].inner_text() if len(job_type_els) > 0 else "N/A"
            salary = await job_type_els[1].inner_text() if len(job_type_els) > 1 else "N/A"

            # Visit job detail page
            job_page = await browser.new_page()
            await job_page.goto(job_url, timeout=60_000)

            try:
                await job_page.wait_for_selector("div.JobView_module_jobDescription", timeout=10_000)
                job_desc_el = await job_page.query_selector("div.JobView_module_jobDescription")
                job_description = await job_desc_el.inner_text() if job_desc_el else "N/A"

                author_el = await job_page.query_selector("p.JobView_module_author")
                author = await author_el.inner_text() if author_el else "N/A"
            except:
                job_description = "N/A"
                author = "N/A"

            await job_page.close()

            jobs.append({
                "title": title,
                "url": job_url,
                "location": location,
                "workplace": workplace,
                "job_type": job_type,
                "salary": salary,
                "description": job_description,
                "author": author
            })

        await browser.close()
        return jobs


def store_in_mongodb(jobs: list, collection_name="motion_jobs"):
    if not jobs:
        return

    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=3000)
    db = client["job_data"]
    db[collection_name].insert_many(jobs)
    print(f"✅ Stored {len(jobs)} jobs in MongoDB collection '{collection_name}'.")


def save_to_json(jobs: list, filename="motion_jobs.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)
    print(f"✅ Saved {len(jobs)} jobs to {filename}")


if __name__ == "__main__":
    scraped_jobs = asyncio.run(scrape_motion_jobs())
    for job in scraped_jobs:
        print("=" * 80)
        for key, value in job.items():
            print(f"{key}: {value}")

    save_to_json(scraped_jobs)
    store_in_mongodb(scraped_jobs)
