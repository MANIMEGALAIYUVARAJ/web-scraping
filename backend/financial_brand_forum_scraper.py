import sys
import os
import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
sys.path.append(os.path.dirname(__file__))
from driver_utils import get_driver

class FinancialBrandForumScraper:
    def __init__(self):
        self.site_name = "Financial Brand Forum"
        self.url = "https://financialbrandforum.com/speakers/"
        self.driver = None

    def setup_driver(self, headless=True):
        self.driver = get_driver(headless=headless)

    def wait_random(self, min_s=1, max_s=3):
        time.sleep(random.uniform(min_s, max_s))

    def scrape(self, query=None, limit=10):
        if not self.driver:
            self.setup_driver()
            
        print(f"Navigating to {self.url}...")
        self.driver.get(self.url)
        
        wait = WebDriverWait(self.driver, 20)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "speaker-modal")))
        self.wait_random(3, 5) # Additional wait for JS rendering
        
        modals = self.driver.find_elements(By.CLASS_NAME, "speaker-modal")
        print(f"Found {len(modals)} speaker modals.")
        
        results = []
        for modal in modals:
            if len(results) >= limit:
                break
                
            try:
                name_elem = modal.find_element(By.CLASS_NAME, "speaker-pop-up-name")
                name = name_elem.get_attribute("textContent").strip()
                role = modal.find_element(By.CLASS_NAME, "speaker-pop-up-title").get_attribute("textContent").strip()
                
                try:
                    bio_elem = modal.find_element(By.CLASS_NAME, "speaker-bio")
                    bio = bio_elem.get_attribute("textContent").strip()
                except: bio = "N/A"
                
                try:
                    sessions = modal.find_elements(By.CLASS_NAME, "session-title")
                    session_list = [s.get_attribute("textContent").strip() for s in sessions if s.get_attribute("textContent").strip()]
                    speaking_sessions = " | ".join(session_list) if session_list else "N/A"
                except: speaking_sessions = "N/A"
                
                item = {
                    'Name': name,
                    'Email ID': 'Not Public',
                    'Role': role,
                    'Role/Designation': role,
                    'Bio': bio,
                    'Speaking Sessions': speaking_sessions,
                    'LinkedIn': 'N/A',
                    'Source URL': self.url
                }
                
                # Standardize Description for UI
                desc = bio
                if speaking_sessions != "N/A":
                    desc += f"\n\nSpeaking Sessions:\n{speaking_sessions}"
                desc += f"\n\nPost URL: {self.url}"
                item['Description'] = desc
                
                # Check query if provided
                if query:
                    searchable = f"{name} {role} {bio} {speaking_sessions}".lower()
                    if query.lower() not in searchable:
                        continue
                        
                results.append(item)
                print(f"✓ Scraped: {name}")
                
            except Exception as e:
                continue
                
        self.driver.quit()
        return results

if __name__ == "__main__":
    scraper = FinancialBrandForumScraper()
    data = scraper.scrape(query="CEO", limit=5)
    print(f"Final results: {len(data)}")
    for d in data:
        print(f" - {d['Name']}: {d['Role']}")
