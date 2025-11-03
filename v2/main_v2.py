import time
import os

from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from scripts import get_jobs_page_html, search_jobs, linkedin_login
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Check if environment variables are set
if not os.getenv("LINKEDIN_USERNAME") or not os.getenv("LINKEDIN_PASSWORD"):
    print("Error: Please configure your LinkedIn credentials in the .env file")
    print("Make sure to create a .env file in the v2 directory with:")
    print("LINKEDIN_USERNAME=your_email@example.com")
    print("LINKEDIN_PASSWORD=your_password")
    exit(1)

options = Options()
options.headless = False
options.add_argument("--disable-blink-features=AutomationControlled")
# Common user-agent; override if needed
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36")

# Helpful flags for Linux / container / headless environments
# - --no-sandbox and --disable-dev-shm-usage are commonly required when running in containers
# - --headless=new uses the new headless mode in newer Chrome; fall back to --headless if needed
if os.getenv("HEADLESS", "0") in ("1", "true", "True"):
    # Chrome new headless mode if supported
    try:
        options.add_argument("--headless=new")
    except Exception:
        options.add_argument("--headless")
    options.add_argument("--disable-gpu")

options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-extensions")
options.add_argument("--disable-background-networking")
options.add_argument("--disable-default-apps")

# Allow specifying custom Chrome/Chromium binary via env var (useful in CI / custom installs)
chrome_bin = os.getenv("CHROME_BIN")
if chrome_bin:
    options.binary_location = chrome_bin

# Create a Service with a chromedriver verbose log path to help debug session failures
service = Service(ChromeDriverManager().install(), log_path="chromedriver.log")
driver = webdriver.Chrome(service=service, options=options)
stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
)
# opening the site first to set domain
driver.get("https://www.linkedin.com/login")  

linkedin_login(driver)
time.sleep(5)  # wait for login to complete


# Finding jobs on LinkedIn
search_jobs(driver, keyword="Data Scientist", location="New York, United States")
print("Job Found")
time.sleep(10)

# Getting page content to scrape jobs later
print("Extracting content of the page...")
html_content = str(get_jobs_page_html(driver))
print("Extractition completed")

# Save the HTML content to a file for later scraping
with open("data/jobs_page.html", "w", encoding="utf-8") as f:
    f.write(html_content)
time.sleep(2)

input()
driver.quit()
# Now you are logged in using saved cookies, proceed to job search and scraping
