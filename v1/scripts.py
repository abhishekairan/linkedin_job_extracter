from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import json
import time
from bs4 import BeautifulSoup

def load_cookies(driver: webdriver.Chrome):
    with open("cookies.json", "r") as f:
        cookies = json.load(f)
        
    valid_keys = ['name', 'value', 'path', 'domain', 'secure', 'httpOnly', 'expiry', 'sameSite']

    for cookie in cookies:
        # Filter the dictionary to only supported keys
        cleaned_cookie = {k: cookie[k] for k in cookie if k in valid_keys}
        if 'expiry' in cleaned_cookie:
            cleaned_cookie['expiry'] = int(cleaned_cookie['expiry'])
        if 'sameSite' not in cleaned_cookie or cleaned_cookie['sameSite'] not in ['Strict', 'Lax', 'None']:
            cleaned_cookie['sameSite'] = 'Lax'
        driver.add_cookie(cleaned_cookie)

    return driver

def search_jobs(driver: webdriver.Chrome, keyword="Python Developer", location="United States"):
    driver.get("https://www.linkedin.com/jobs")
    time.sleep(3)

    job_search_input = driver.find_element(By.CSS_SELECTOR, "input[componentkey='jobSearchBox']")
    job_search_input.clear()
    job_search_input.send_keys(keyword)
    job_search_input.send_keys(Keys.RETURN)


def linkedin_login(driver: webdriver.Chrome, username: str= "cubicfammy@gmail.com", password: str="9f6aZq~@.#K7h$!"):
    time.sleep(2)
    username_input = driver.find_element(By.ID, "username")
    password_input = driver.find_element(By.ID, "password")

    username_input.send_keys(username)
    time.sleep(2)
    password_input.send_keys(password)
    time.sleep(0.5)
    password_input.send_keys(Keys.RETURN)

def get_jobs_page_html(driver: webdriver.Chrome):
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    content = soup.find('main',id="main")
    return content


if __name__ == "__main__":
    pass