import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from DB.db import insert_raw_link

def extract_long_title_links(url):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get(url)
        time.sleep(10)  # Wait for 10 seconds before parsing
        links = driver.find_elements(By.TAG_NAME, 'a')
        long_title_links = []
        for link in links:
            href = link.get_attribute('href')
            title = link.get_attribute('title')
            if href and title and len(title) > 50:
                long_title_links.append({'title': title, 'article_url': href})
        # Remove duplicates based on title and article_url
        seen = set()
        unique_links = []
        for link in long_title_links:
            key = (link['title'], link['article_url'])
            if key not in seen:
                seen.add(key)
                unique_links.append(link)
        return unique_links
    finally:
        driver.quit()

if __name__ == '__main__':
    url = "https://www.indiatoday.in/"
    links = extract_long_title_links(url)
    print('Links with title attribute longer than 50 characters:')
    print(links)
    for link in links:
        print(f"Title: {link['title']} | Href: {link['article_url']}")
        insert_raw_link(link['title'], link['article_url'])
