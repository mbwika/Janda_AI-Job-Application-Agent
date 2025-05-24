import requests
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse

def fetch_and_parse_robots(domain):
    # Ensure domain has scheme
    if not domain.startswith("http"):
        domain = "https://" + domain

    parsed = urlparse(domain)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    print(f"\nFetching robots.txt from: {robots_url}")

    try:
        response = requests.get(robots_url, timeout=10)
        if response.status_code != 200:
            print("❌ Failed to fetch robots.txt")
            return

        content = response.text
        lines = content.splitlines()

        user_agent = None
        disallow_rules = {}

        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.lower().startswith("user-agent:"):
                user_agent = line.split(":")[1].strip()
                disallow_rules[user_agent] = []
            elif line.lower().startswith("disallow:") and user_agent:
                path = line.split(":", 1)[1].strip()
                disallow_rules[user_agent].append(path)

        for ua, rules in disallow_rules.items():
            print(f"\n🧠 User-agent: {ua}")
            if not rules:
                print("✅ No disallowed paths.")
            else:
                for rule in rules:
                    print(f"⛔ Disallow: {rule}")

    except Exception as e:
        print(f"❌ Error: {e}")

# Example usage
job_sites = [
    # "https://flexjobs.com",
    # "https://www.us.jobrapido.com",
    "https://careers.ey.com/ey/",
    "https://jobs.us.pwc.com/"
    # "https://www.kpmg.com/us/en/home/careers.html",
    # "https://www.kpmguscareers.com/",
    # "https://www.deloitte.com/us/en/careers.html",
    # "https://www.bain.com/careers/",
    # "https://www.mckinsey.com/careers",
    # "https://www.bcg.com/careers",
    # "https://www.accenture.com/us-en/careers",
    # "https://www.capgemini.com/us-en/careers/",
    # "https://www.ibm.com/employment/",
    # "https://www.oracle.com/corporate/careers/",
    # "https://www.sap.com/about/careers.html",
    # "https://www.salesforce.com/company/careers/",
    # "https://www.microsoft.com/en-us/careers",
    # "https://www.google.com/about/careers/",
    # "https://www.amazon.jobs/en/",
    # "https://www.apple.com/jobs/us/",
    # "https://www.facebook.com/careers/",
    # "https://www.twitter.com/careers",
    # "https://www.linkedin.com/company/linkedin/jobs/",
    # "https://www.netflix.com/jobs",
    # "https://www.spotifyjobs.com/",
    # "https://www.airbnb.com/careers",
    # "https://www.uber.com/us/en/careers/",
    # "https://www.lyft.com/careers",
    # "https://www.snap.com/en-US/jobs/",
    # "https://www.pinterest.com/jobs/",
    # "https://www.tumblr.com/jobs",
    # "https://www.reddit.com/r/redditjobs/",
    # "https://www.quora.com/careers",
    # "https://www.yelp.com/careers",
    # "https://www.zillow.com/careers/",
    # "https://www.indeed.com",
    # "https://www.linkedin.com",
    # "https://www.glassdoor.com",
    # "https://remoteok.com",
    # "https://weworkremotely.com",
    # "https://angel.co/jobs",
    # "https://www.simplyhired.com",
    # "https://www.monster.com",
    # "https://www.ziprecruiter.com",
    # "https://www.jobvite.com",
    # "https://www.hired.com",
    # "https://www.workable.com",
    # "https://www.upwork.com",
    # "https://www.fiverr.com",
    # "https://www.toptal.com",
    # "https://www.freelancer.com",
    # "https://www.peopleperhour.com",
    # "https://www.remotive.com",
    # "https://www.jobbatical.com",
    # "https://www.jobspring.io",
    # "https://www.careerbuilder.com",
    # "https://www.jobcase.com",
    # "https://www.snagajob.com",
    # "https://www.careerjet.com",
    # "https://www.jobs2careers.com",
    # "https://www.careerbliss.com",
    # "https://www.jobsearch.com",
    # "https://www.jobhero.com",
    # "https://www.jobscan.co"
]

for site in job_sites:
    fetch_and_parse_robots(site)
# This script fetches and parses the robots.txt file from a list of job sites.
# It extracts the user-agent and disallow rules, printing them in a readable format.
# The script uses the requests library to make HTTP requests and the urllib library to parse URLs.
# It handles exceptions and prints error messages if the robots.txt file cannot be fetched.
# The script is designed to be run in a Python environment with internet access.
# The script is useful for web scraping and understanding the crawling policies of different job sites.
# The script can be modified to include more job sites or to save the results to a file.
# The script can be run as a standalone program or imported as a module in other Python scripts.
# The script can be extended to include more advanced features such as rate limiting, user-agent rotation, and handling CAPTCHAs.
# The script can be used as a starting point for building a web scraper for job listings.
# The script can be modified to include more advanced features such as handling cookies, sessions, and authentication.
# The script can be used as a reference for understanding how to fetch and parse robots.txt files.