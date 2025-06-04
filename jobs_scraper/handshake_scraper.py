# Chrome Browser Scraper for Handshake Job Listings
# This script uses Playwright to scrape job listings from Handshake.
# It requires a pre-existing Chrome profile that is already logged in to Handshake.
# It scrapes job details including company, title, location, date posted, and job description.
# Linux Launch Chrome command: google-chrome --user-data-dir=/home/smartcat/chrome-handshake-profile

import asyncio
import json
import re
from playwright.async_api import async_playwright

BASE_URL = "https://utdallas.joinhandshake.com"
SEARCH_URL_TEMPLATE = BASE_URL + "/job-search?page={}"
JOB_CONTAINER_SELECTOR = "div[data-hook^='job-result-card']"
USER_DATA_DIR = "/home/smartcat/chrome-handshake-profile"

START_PAGE = 1
END_PAGE = 1  # You can increase this to scrape more pages

async def scrape_handshake_jobs():
    all_jobs = []

    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False
        )

        page = browser.pages[0] if browser.pages else await browser.new_page()
        await page.goto(BASE_URL, timeout=60000)

        # Confirm login
        if "login" in page.url.lower():
            print("⚠️ Not logged in. Please log in manually with this profile.")
            await browser.close()
            return []

        for page_number in range(START_PAGE, END_PAGE + 1):
            search_url = SEARCH_URL_TEMPLATE.format(page_number)
            print(f"\n🔄 Scraping search results page {page_number}: {search_url}")

            try:
                await page.goto(search_url, timeout=60000)
                await page.wait_for_selector(JOB_CONTAINER_SELECTOR, timeout=30000)
            except Exception as e:
                print(f"❌ Failed to load page {page_number}: {e}")
                continue

            job_cards = await page.query_selector_all(JOB_CONTAINER_SELECTOR)
            print(f"➡️ Found {len(job_cards)} job cards on page {page_number}")

            for card in job_cards:
                try:
                    data_hook = await card.get_attribute("data-hook")
                    match = re.search(r'job-result-card\s*\|\s*(\d+)', data_hook or "")
                    if not match:
                        continue

                    job_id = match.group(1).strip()
                    job_detail_url = f"{BASE_URL}/job-search/{job_id}?per_page=5&sort=posted_date_desc&page={page_number}"

                    job_page = await browser.new_page()
                    try:
                        await job_page.goto(job_detail_url, timeout=60000)
                        print(f"🔍 Scraping job details for ID {job_id} at {job_detail_url}")
                        await job_page.wait_for_selector(JOB_CONTAINER_SELECTOR, timeout=30000)
                        job_detail_cards = await job_page.query_selector_all(JOB_CONTAINER_SELECTOR)

                        for detail_card in job_detail_cards:
                            company_elem = await detail_card.query_selector("div.sc-iTFTee.kqrVpX span.sc-jrcTuL.ifJtBF")
                            title_elem = await detail_card.query_selector("div.sc-hLBbgP.dpzvOf")
                            location_elem = await detail_card.query_selector("span.sc-hywjFt.eqqBly")
                            date_elem = await detail_card.query_selector("span.sc-qyDQW.ZEwse")
                            link_elem = await detail_card.query_selector("a[href*='/jobs/']")

                            job_url = BASE_URL + (await link_elem.get_attribute("href") or "") if link_elem else ""
                            search_id_match = re.search(r'searchId=([a-f0-9\-]+)', job_url)
                            print(f"🔗 Job URL: {search_id_match}")
                            search_uuid = search_id_match.group(1) if search_id_match else ""

                            job_data = {
                                "company": (await company_elem.inner_text()).strip() if company_elem else "",
                                "title": (await title_elem.inner_text()).strip() if title_elem else "",
                                "location": (await location_elem.inner_text()).strip() if location_elem else "",
                                "date_posted": (await date_elem.inner_text()).strip() if date_elem else "",
                                "job_url": job_detail_url,
                                "search_uuid": search_uuid,
                                "job_id": job_id
                            }

                            # 🔍 Visit job detail page for description
                            if job_detail_url:
                                desc_page = await browser.new_page()
                                try:
                                    await desc_page.goto(job_detail_url, timeout=60000)
                                    print(f"🔍 Loading job description for {job_detail_url}")
                                    # try:
                                    #     view_more_btn = await desc_page.query_selector("button.view-more-button")
                                    #     if view_more_btn:
                                    #         await view_more_btn.click()
                                    #         await desc_page.wait_for_timeout(500)
                                    # except:
                                    #     pass

                                    await desc_page.wait_for_selector("div.sc-hpHAyN.gFYNTb", timeout=30000)
                                    desc_elem = await desc_page.query_selector("div.sc-hpHAyN.gFYNTb")
                                    job_data["description"] = (await desc_elem.text_content()).strip() if desc_elem else ""
                                except Exception as e:
                                    print(f"❌ Failed to load job description for {search_id_match}: {e}")
                                    job_data["description"] = ""
                                finally:
                                    await desc_page.close()

                            all_jobs.append(job_data)

                    except Exception as e:
                        print(f"⚠️ Failed to scrape job detail for ID {job_id}: {e}")
                    finally:
                        await job_page.close()

                except Exception as e:
                    print(f"⚠️ Error processing job card: {e}")
                    continue

        await browser.close()
        return all_jobs

if __name__ == "__main__":
    scraped_jobs = asyncio.run(scrape_handshake_jobs())
    with open("handshake_jobs.json", "w") as f:
        json.dump(scraped_jobs, f, indent=2)
    print(f"\n✅ Scraped {len(scraped_jobs)} jobs.")


# import asyncio
# from playwright.async_api import async_playwright
# import json
# import re

# BASE_URL = "https://utdallas.joinhandshake.com"
# JOB_CONTAINER_SELECTOR = "div[data-hook^='job-result-card']"
# PROFILE_DIR = "/home/smartcat/chrome-handshake-profile"
# START_PAGE = 1
# END_PAGE = 5  # Adjust as needed, recommended max is 300

# async def extract_random_digits(page):
#     await page.goto(BASE_URL + "/job-search", timeout=60000)
#     await page.wait_for_selector(JOB_CONTAINER_SELECTOR, timeout=30000)

#     # Find the first job card and extract its `data-hook`
#     job_card = await page.query_selector(JOB_CONTAINER_SELECTOR)
#     if job_card:
#         data_hook = await job_card.get_attribute("data-hook")
#         match = re.search(r'job-result-card\s*\|\s*(\d+)', data_hook or "")
#         if match:
#             return match.group(1)

#     raise ValueError("Could not extract [random-digits] from data-hook.")

# async def scrape_handshake_jobs():
#     all_jobs = []

#     async with async_playwright() as p:
#         browser = await p.chromium.launch_persistent_context(
#             user_data_dir=PROFILE_DIR,
#             headless=False
#         )

#         context = browser
#         pages = context.pages
#         page = pages[0] if pages else await context.new_page()

#         # Confirm login
#         await page.goto(BASE_URL, timeout=60000)
#         if "login" in page.url.lower():
#             print("⚠️ Not logged in. Please log in manually with this profile.")
#             await browser.close()
#             return []

#         # Extract the dynamic [random-digits] from the job cards
#         print("🔍 Extracting dynamic job search ID ([random-digits])...")
#         search_id = await extract_random_digits(page)
#         print(f"✅ Found job search ID: {search_id}")

#         for page_number in range(START_PAGE, END_PAGE + 1):
#             search_url = f"{BASE_URL}/job-search/{search_id}?per_page=25&sort=posted_date_desc&page={page_number}"
#             print(f"🔄 Scraping page {page_number}: {search_url}")
#             try:
#                 await page.goto(search_url, timeout=60000)
#                 await page.wait_for_selector(JOB_CONTAINER_SELECTOR, timeout=30000)
#             except Exception as e:
#                 print(f"❌ Navigation error on page {page_number}: {e}")
#                 continue

#             job_cards = await page.query_selector_all(JOB_CONTAINER_SELECTOR)
#             for card in job_cards:
#                 try:
#                     company_elem = await card.query_selector("div.sc-iTFTee.kqrVpX span.sc-jrcTuL.ifJtBF")
#                     company = await company_elem.inner_text() if company_elem else ""

#                     title_elem = await card.query_selector("div.sc-hLBbgP.dpzvOf")
#                     title = await title_elem.inner_text() if title_elem else ""

#                     location_elem = await card.query_selector("span.sc-hywjFt.eqqBly")
#                     location = await location_elem.inner_text() if location_elem else ""

#                     date_elem = await card.query_selector("span.sc-qyDQW.ZEwse")
#                     date_posted = await date_elem.inner_text() if date_elem else ""

#                     link_elem = await card.query_selector("a[href*='/jobs/']")
#                     href = await link_elem.get_attribute("href") if link_elem else ""

#                     # Extract job ID and searchId UUID
#                     job_url = BASE_URL + href if href else ""
#                     search_id_match = re.search(r'searchId=([a-f0-9\-]+)', href or "")
#                     search_uuid = search_id_match.group(1) if search_id_match else ""

#                     job_data = {
#                         "company": company.strip(),
#                         "title": title.strip(),
#                         "location": location.strip(),
#                         "date_posted": date_posted.strip(),
#                         "job_url": job_url,
#                         "search_uuid": search_uuid
#                     }

#                     if job_url:
#                         job_page = await context.new_page()
#                         try:
#                             await job_page.goto(job_url, timeout=60000)
#                             await job_page.wait_for_selector("div.sc-hpHAyN.gFYNTb", timeout=30000)
#                             desc_container = await job_page.query_selector("div.sc-hpHAyN.gFYNTb")
#                             description = await desc_container.inner_text() if desc_container else ""
#                             job_data["description"] = description.strip()
#                         except Exception as e:
#                             job_data["description"] = ""
#                             print(f"❌ Failed to get description for {job_url}: {e}")
#                         await job_page.close()

#                     all_jobs.append(job_data)
#                 except Exception as e:
#                     print(f"❌ Error processing job card: {e}")
#                     continue

#         await browser.close()
#         return all_jobs

# if __name__ == "__main__":
#     scraped_jobs = asyncio.run(scrape_handshake_jobs())
#     with open("handshake_jobs.json", "w") as f:
#         json.dump(scraped_jobs, f, indent=2)
#     print(f"✅ Scraped {len(scraped_jobs)} jobs.")


# import asyncio
# from playwright.async_api import async_playwright
# import json

# BASE_URL = "https://utdallas.joinhandshake.com"
# SEARCH_URL_TEMPLATE = BASE_URL + "/job-search/9864589?per_page=25&sort=posted_date_desc&page={}"
# START_PAGE = 1
# END_PAGE = 300
# JOB_CONTAINER_SELECTOR = "div[data-hook^='job-result-card']"

# # Path to the Chrome profile that is already logged in
# USER_DATA_DIR = "/home/smartcat/chrome-handshake-profile"

# async def scrape_handshake_jobs():
#     all_jobs = []

#     async with async_playwright() as p:
#         # Launch browser with the logged-in user profile
#         browser = await p.chromium.launch_persistent_context(
#             user_data_dir=USER_DATA_DIR,
#             headless=False
#         )

#         # Reuse the first tab, or open a new one if none exists
#         context = browser
#         pages = context.pages
#         page = pages[0] if pages else await context.new_page()

#         # Check if still logged in
#         await page.goto(BASE_URL, timeout=60000)
#         if "login" in page.url.lower():
#             print("⚠️ Still redirected to login. Please log in manually first.")
#             await browser.close()
#             return []

#         # Start scraping job listings
#         for page_number in range(START_PAGE, END_PAGE + 1):
#             url = SEARCH_URL_TEMPLATE.format(page_number)
#             print(f"Scraping page {page_number}: {url}")
#             try:
#                 await page.goto(url, timeout=60000)
#                 await page.wait_for_selector(JOB_CONTAINER_SELECTOR, timeout=60000)
#             except Exception as e:
#                 print(f"⏱ Timeout or navigation error on page {page_number}: {e}")
#                 continue

#             job_cards = await page.query_selector_all(JOB_CONTAINER_SELECTOR)
#             for card in job_cards:
#                 try:
#                     company_elem = await card.query_selector("div.sc-iTFTee.kqrVpX span.sc-jrcTuL.ifJtBF")
#                     company = await company_elem.inner_text() if company_elem else ""

#                     title_elem = await card.query_selector("div.sc-hLBbgP.dpzvOf")
#                     title = await title_elem.inner_text() if title_elem else ""

#                     location_elem = await card.query_selector("span.sc-hywjFt.eqqBly")
#                     location = await location_elem.inner_text() if location_elem else ""

#                     date_elem = await card.query_selector("span.sc-qyDQW.ZEwse")
#                     date_posted = await date_elem.inner_text() if date_elem else ""

#                     link_elem = await card.query_selector("a[href*='/jobs/']")
#                     job_relative_link = await link_elem.get_attribute("href") if link_elem else ""
#                     job_url = BASE_URL + job_relative_link if job_relative_link else ""

#                     job_data = {
#                         "company": company.strip(),
#                         "title": title.strip(),
#                         "location": location.strip(),
#                         "date_posted": date_posted.strip(),
#                         "job_url": job_url
#                     }

#                     # Visit job detail page for description
#                     if job_url:
#                         job_page = await context.new_page()
#                         try:
#                             await job_page.goto(job_url, timeout=60000)
#                             await job_page.wait_for_selector("div.sc-hpHAyN.gFYNTb", timeout=30000)
#                             desc_container = await job_page.query_selector("div.sc-hpHAyN.gFYNTb")
#                             description = await desc_container.inner_text() if desc_container else ""
#                             job_data["description"] = description.strip()
#                         except Exception as e:
#                             job_data["description"] = ""
#                             print(f"❌ Failed to load description for {job_url}: {e}")
#                         await job_page.close()

#                     all_jobs.append(job_data)
#                 except Exception as e:
#                     print(f"❌ Error parsing job card: {e}")
#                     continue

#         await browser.close()
#     return all_jobs


# if __name__ == "__main__":
#     scraped_jobs = asyncio.run(scrape_handshake_jobs())
#     with open("handshake_jobs.json", "w") as f:
#         json.dump(scraped_jobs, f, indent=2)
#     print(f"✅ Scraped {len(scraped_jobs)} jobs.")
