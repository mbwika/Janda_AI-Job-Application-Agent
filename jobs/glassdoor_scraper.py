import asyncio
import json
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup


async def scrape_glassdoor_jobs(base_url: str, max_pages: int = 3):
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto(base_url, timeout=120_000)
        await page.wait_for_selector("ul.JobsList_jobsList_IqjTr", timeout=60_000)

        for _ in range(max_pages):
            content = await page.content()
            soup = BeautifulSoup(content, "html.parser")

            job_cards = soup.select("li[data-test='jobListing']")
            for job in job_cards:
                job_data = {}
                try:
                    employer_elem = job.select_one("span.EmployerProfile_compactEmployerName__9MGcV")
                    job_data["employer"] = employer_elem.text.strip() if employer_elem else None
                    title_elem = job.select_one("a[data-test='job-title']")
                    job_data["title"] = title_elem.text.strip() if title_elem else None
                    location_elem = job.select_one("div[data-test='emp-location']")
                    job_data["location"] = location_elem.text.strip() if location_elem else None

                    salary_tag = job.select_one("div[data-test='detailSalary']")
                    if salary_tag:
                        job_data["salary"] = salary_tag.get_text(separator=" ", strip=True)

                    job_link = job.select_one("a[data-test='job-title']")["href"]
                    if not job_link.startswith("http"):
                        job_link = "https://www.glassdoor.com" + job_link
                    job_data["link"] = job_link

                    # Visit job link to get full description
                    detail_page = await context.new_page()
                    await detail_page.goto(job_link, timeout=60000)
                    await detail_page.wait_for_selector("div.JobDetails_jobDescription_uW_fk", timeout=10000)
                    job_html = await detail_page.content()
                    detail_soup = BeautifulSoup(job_html, "html.parser")
                    desc_block = detail_soup.select_one("div.JobDetails_jobDescription_uW_fk")
                    if desc_block:
                        job_data["description"] = desc_block.get_text(separator="\n", strip=True)
                    await detail_page.close()

                    results.append(job_data)
                except Exception as e:
                    print(f"Error extracting job: {e}")
                    continue

            # Pagination
            next_btn = await page.query_selector("button[aria-label='Next']")
            if next_btn:
                await next_btn.click()
                await page.wait_for_load_state("networkidle")
            else:
                break

        await browser.close()

    return results


if __name__ == "__main__":
    # base_url = "https://www.glassdoor.com/Job/united-states-jobs-SRCH_IL.0,13_IN1.htm"
    base_url = "https://www.glassdoor.com/Job/index.htm"
    scraped_jobs = asyncio.run(scrape_glassdoor_jobs(base_url))
    with open("glassdoor_jobs.json", "w", encoding="utf-8") as f:
        json.dump(scraped_jobs, f, indent=2, ensure_ascii=False)
    print(f"Scraped {len(scraped_jobs)} jobs.")
