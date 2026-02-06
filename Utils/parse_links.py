import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from DB.db import insert_raw_link

def extract_long_title_links(url):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=chrome_options)
    try:
        print(f"Fetching URL: {url}")
        driver.get(url)
        
        # Wait for page to load and dynamic content to appear
        print("Waiting for page content to load...")
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, 'a'))
            )
        except:
            print("Timeout waiting for links, continuing anyway...")
        
        time.sleep(5)  # Additional wait for lazy loading
        
        links = driver.find_elements(By.TAG_NAME, 'a')
        print(f"Found {len(links)} total links on the page")
        
        long_title_links = []
        for link in links:
            href = link.get_attribute('href')
            title = link.get_attribute('title')
            text = link.text.strip()
            
            # Use title attribute if available, otherwise use link text
            link_title = title or text
            
            # Filter links with meaningful titles (longer than 50 chars)
            if href and link_title and len(link_title) > 50:
                long_title_links.append({'title': link_title, 'article_url': href})
                
        print(f"Found {len(long_title_links)} links with titles > 50 characters")
        
        # Remove duplicates based on title and article_url
        seen = set()
        unique_links = []
        for link in long_title_links:
            key = (link['title'], link['article_url'])
            if key not in seen:
                seen.add(key)
                unique_links.append(link)
        
        print(f"Found {len(unique_links)} unique links")
        return unique_links
    except Exception as e:
        print(f"Error extracting links: {e}")
        return []
    finally:
        driver.quit()

if __name__ == '__main__':
    url = "https://www.livemint.com/"
    links = extract_long_title_links(url)
    print('\nLinks with title attribute longer than 50 characters:')
    print(links)
    if links:
        for link in links:
            print(f"Title: {link['title'][:60]}... | Href: {link['article_url']}")
            insert_raw_link(link['title'], link['article_url'])
    else:
        print("No links found! The page may require special handling or JavaScript rendering.")
