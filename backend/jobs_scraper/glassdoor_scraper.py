
import asyncio
import json
from playwright.async_api import async_playwright

SEARCH_URL = "https://www.glassdoor.com/job-listing/sr-backend-developer-node-js-aws-mongodb-resolve-tech-solutions-inc-JV_IC1140006_KO0,40_KE41,67.htm?jl=1009754088983"

async def scrape_glassdoor_jobs():
    jobs = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        page = await browser.new_page()
        await page.goto(SEARCH_URL, timeout=120_000)

        try:
            await page.wait_for_selector("div[data-test='JobListing']", timeout=60_000)
        except Exception as e:
            print("Failed to load job listings:", e)
            await browser.close()
            return jobs

        job_cards = await page.query_selector_all("a.JobCard_jobTitle__GLyJ1")
        print(f"Found {len(job_cards)} job listings.")

        for job_card in job_cards:
            try:
                job_link = await job_card.get_attribute("href")
                job_url = f"https://www.glassdoor.com{job_link}" if job_link and job_link.startswith("/") else job_link
                job_id = job_link.split("jl=")[-1] if "jl=" in job_link else ""

                title = await job_card.inner_text()

                container = await job_card.evaluate_handle("node => node.closest('div[data-test=\"JobListing\"]')")
                company_el = await container.query_selector("span.EmployerProfile_compactEmployerName__9MGcV")
                location_el = await container.query_selector(f"div#job-location-{job_id}")
                salary_el = await container.query_selector(f"div#job-salary-{job_id}")
                salary_by_el = await container.query_selector(f"div#job-salary-{job_id} span")

                job = {
                    "company": await company_el.inner_text() if company_el else None,
                    "job-title": title,
                    "job-link": job_url,
                    "job-location": await location_el.inner_text() if location_el else None,
                    "job-salary": await salary_el.inner_text() if salary_el else None,
                    "salary-estimate-by": await salary_by_el.inner_text() if salary_by_el else None,
                }

                # Visit job URL and scrape full description
                job_page = await browser.new_page()
                await job_page.goto(job_url, timeout=120_000)
                try:
                    await job_page.wait_for_selector("div.JobDetails_jobDescription_uW_fk.JobDetails_showHidden_C_FOA p", timeout=30_000)
                    paragraphs = await job_page.query_selector_all("div.JobDetails_jobDescription_uW_fk.JobDetails_showHidden_C_FOA p")
                    job["description"] = " ".join([await p.inner_text() for p in paragraphs])
                except Exception as e:
                    print(f"Failed to load description for {job_url}: {e}")
                    job["description"] = None
                await job_page.close()

                jobs.append(job)
            except Exception as e:
                print(f"Error scraping a job card: {e}")
                continue

        await browser.close()
    return jobs

if __name__ == "__main__":
    scraped_jobs = asyncio.run(scrape_glassdoor_jobs())
    with open("glassdoor_jobs.json", "w", encoding="utf-8") as f:
        json.dump(scraped_jobs, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(scraped_jobs)} jobs to glassdoor_jobs.json")


# from pathlib import Path

# # Create a Python script for scraping Glassdoor job board details and job descriptions
# glassdoor_scraper_code = ""
# import asyncio
# import json
# import re
# from playwright.async_api import async_playwright

# BASE_URL = "https://www.glassdoor.com/Job/index.htm"

# async def scrape_glassdoor_jobs():
#     jobs = []
#     async with async_playwright() as p:
#         browser = await p.chromium.launch(headless=True)
#         page = await browser.new_page()
#         await page.goto(BASE_URL, timeout=120_000)
#         await page.wait_for_selector("a.JobCard_jobTitle__GLyJ1", timeout=60_000)

#         job_cards = await page.query_selector_all("a.JobCard_jobTitle__GLyJ1")
#         print(f"Found {len(job_cards)} job listings.")

#         for job_card in job_cards:
#             job_link = await job_card.get_attribute("href")
#             job_url = f"https://www.glassdoor.com{job_link}" if job_link.startswith("/") else job_link
#             job_id = job_link.split("jl=")[-1] if "jl=" in job_link else ""

#             company_selector = f"span.EmployerProfile_compactEmployerName__9MGcV"
#             location_selector = f"div#job-location-{job_id}.JobCard_location__Ds1fM"
#             salary_selector = f"div#job-salary-{job_id}.JobCard_salaryEstimate__QpbTW"
#             salary_estimate_by_selector = f"div#job-salary-{job_id}.JobCard_salaryEstimate__QpbTW span"

#             company_el = await job_card.evaluate_handle("node => node.closest('div').querySelector('span.EmployerProfile_compactEmployerName__9MGcV')")
#             location_el = await page.query_selector(location_selector)
#             salary_el = await page.query_selector(salary_selector)
#             salary_by_el = await page.query_selector(salary_estimate_by_selector)

#             job = {
#                 "company": await company_el.inner_text() if company_el else None,
#                 "job-title": await job_card.inner_text(),
#                 "job-link": job_url,
#                 "job-location": await location_el.inner_text() if location_el else None,
#                 "job-salary": await salary_el.inner_text() if salary_el else None,
#                 "salary-estimate-by": await salary_by_el.inner_text() if salary_by_el else None,
#             }

#             # Visit job URL to get full description
#             job_page = await browser.new_page()
#             await job_page.goto(job_url, timeout=120_000)
#             try:
#                 await job_page.wait_for_selector("div.JobDetails_jobDescription_uW_fk.JobDetails_showHidden_C_FOA p", timeout=60_000)
#                 paragraphs = await job_page.query_selector_all("div.JobDetails_jobDescription_uW_fk.JobDetails_showHidden_C_FOA p")
#                 job["description"] = " ".join([await p.inner_text() for p in paragraphs])
#             except Exception as e:
#                 print(f"Failed to load job description for {job_url}: {e}")
#                 job["description"] = None

#             await job_page.close()
#             jobs.append(job)

#         await browser.close()

#     return jobs

# if __name__ == "__main__":
#     scraped_jobs = asyncio.run(scrape_glassdoor_jobs())
#     with open("glassdoor_jobs.json", "w", encoding="utf-8") as f:
#         json.dump(scraped_jobs, f, ensure_ascii=False, indent=2)


# # Write the scraper code to a file
# file_path = Path("glassdoor_scraper.py")
# file_path.write_text(glassdoor_scraper_code)
# file_path

# Uncomment the following lines to run the scraper directly
# Uncomment the following lines to run the scraper directly
# if __name__ == "__main__":
#     scraped_jobs = asyncio.run(scrape_glassdoor_jobs())
#     for job in scraped_jobs:
#         print("="*80)
#         for key, value in job.items():
#             print(f"{key}: {value}")
#     # Export to JSON