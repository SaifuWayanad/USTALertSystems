import json
import time
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def read_webpage_content(url: str) -> str:
    """
    Open webpage with Selenium, wait for JS to load,
    parse HTML, and return clean readable content (text only).
    """

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    try:
        driver.get(url)

        # Wait for JS content to load
        time.sleep(5)

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        # Remove noise
        for tag in soup(["script", "style", "nav", "footer", "noscript", "header", "aside", "form", "iframe", "svg", "canvas", "input", "button", "figure", "figcaption", "link", "meta"]):
            tag.decompose()

        # Extract readable text only
        text = " ".join(soup.get_text(separator=" ").split())
        # print(text)
        return text

    finally:
        driver.quit()
