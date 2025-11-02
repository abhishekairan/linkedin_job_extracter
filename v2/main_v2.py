from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.chrome.options import Options
from scripts import get_jobs_page_html, search_jobs, linkedin_login
import time

options = Options()
options.headless = False
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36")
driver = webdriver.Chrome(options=options)
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
