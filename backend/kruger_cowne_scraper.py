import sys
import os
import time
import random
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
sys.path.append(os.path.dirname(__file__))
from driver_utils import get_driver

class KrugerCowneScraper:
    def __init__(self):
        self.site_name = "Kruger Cowne"
        self.base_url = "https://krugercowne.com/speaker-topics/finance/"
        self.driver = None

    def setup_driver(self, headless=True):
        self.driver = get_driver(headless=headless)

    def wait_random(self, min_s=1, max_s=3):
        time.sleep(random.uniform(min_s, max_s))

    def scrape(self, query=None, limit=10):
        if not self.driver:
            self.setup_driver()

        print(f"Navigating to {self.base_url}...")
        self.driver.get(self.base_url)
        
        wait = WebDriverWait(self.driver, 20)
        try:
            # Wait for listing items
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "jet-listing-grid__item")))
        except:
            print("Listing items not found or page took too long to load.")
            return []

        self.wait_random(2, 4)
        
        # Extract profile links
        items = self.driver.find_elements(By.CLASS_NAME, "jet-listing-grid__item")
        profile_links = []
        for item in items:
            try:
                link_elem = item.find_element(By.TAG_NAME, "a")
                href = link_elem.get_attribute("href")
                if href and "/talent/" in href:
                    profile_links.append(href)
            except: continue
        
        # Remove duplicates
        profile_links = list(dict.fromkeys(profile_links))
        print(f"Found {len(profile_links)} potential profile links.")

        results = []
        for link in profile_links:
            if len(results) >= limit:
                break
            
            print(f"Scraping profile: {link}")
            try:
                self.driver.get(link)
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
                self.wait_random(2, 3)
                
                # Use textContent for broad capture
                def get_text(selector, by=By.CSS_SELECTOR):
                    try:
                        elem = self.driver.find_element(by, selector)
                        return elem.get_attribute("textContent").strip()
                    except: return "N/A"

                name = get_text("h1.jet-listing-dynamic-field__content")
                if name == "N/A": 
                    name = get_text(".elementor-heading-title")
                
                # Role is often the next line or a specific subtitle
                role = "N/A"
                try:
                    role_elem = self.driver.find_element(By.XPATH, "//h1/following::div[contains(@class, 'jet-listing-dynamic-field')]")
                    role = role_elem.get_attribute("textContent").strip()
                except: pass
                
                # Bio
                bio = "N/A"
                try:
                    # Look for the section with 'About' or 'Long Bio'
                    bio_elems = self.driver.find_elements(By.CSS_SELECTOR, ".jet-listing-dynamic-field__content p")
                    if bio_elems:
                        bio = "\n".join([p.get_attribute("textContent").strip() for p in bio_elems if len(p.get_attribute("textContent")) > 20])
                except: pass
                
                # Phone
                phone = "N/A"
                try:
                    phone_elem = self.driver.find_element(By.XPATH, "//a[contains(@href, 'tel:')]")
                    phone = phone_elem.get_attribute("textContent").strip()
                    # Clean up phone text (e.g. "+44 (0) 203..." from "To book... call +44...")
                    phone_match = re.search(r'(\+?\d[\d\s\(\)]+)', phone)
                    if phone_match: phone = phone_match.group(1).strip()
                except: pass
                
                # Email - Generic text search as it's often in footer or contact section
                email = "Not Public"
                try:
                    page_text = self.driver.find_element(By.TAG_NAME, "body").text
                    email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', page_text)
                    if email_match: email = email_match.group(0)
                except: pass

                item = {
                    'Name': name,
                    'Email ID': email,
                    'Role/Designation': role,
                    'Bio': bio,
                    'Description': bio,
                    'Contact Number': phone,
                    'Speaking Sessions': 'N/A',
                    'LinkedIn': 'N/A',
                    'Source URL': link
                }
                
                # Query filtering
                if query:
                    searchable = f"{name} {role} {bio}".lower()
                    if query.lower() not in searchable:
                        continue
                
                results.append(item)
                print(f"✓ Scraped: {name}")
                
            except Exception as e:
                print(f"Error scraping {link}: {e}")
                continue
                
        self.driver.quit()
        return results

if __name__ == "__main__":
    scraper = KrugerCowneScraper()
    results = scraper.scrape(limit=2)
    import json
    print(json.dumps(results, indent=2))
