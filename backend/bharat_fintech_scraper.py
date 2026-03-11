import time
import random
import os
import csv
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import sys
import argparse
from fake_useragent import UserAgent

class StealthConfig:
    """Helper to configure Chrome with anti-detection settings"""
    @staticmethod
    def get_random_resolution():
        resolutions = ["1920,1080", "1600,900", "1536,864", "1440,900", "1366,768"]
        return random.choice(resolutions)

    @staticmethod
    def get_random_language():
        languages = ["en-US,en;q=0.9", "en-GB,en;q=0.8", "en-CA,en;q=0.7"]
        return random.choice(languages)

class HumanBehavior:
    """Simulate human behavior to bypass bot detection"""
    @staticmethod
    def random_delay(min_sec=2, max_sec=5):
        time.sleep(random.uniform(min_sec, max_sec))

    @staticmethod
    def human_scroll(driver):
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            # Scroll down in random increments
            scroll_step = random.randint(300, 700)
            current_pos = 0
            # Exhaustive scroll to ensure all lazy-loaded items are triggered
            while current_pos < last_height:
                current_pos += scroll_step
                driver.execute_script(f"window.scrollTo(0, {current_pos});")
                time.sleep(random.uniform(0.2, 0.5))
            
            time.sleep(3)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                # One last big scroll and wait
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(5)
                if driver.execute_script("return document.body.scrollHeight") == last_height:
                    break
            last_height = new_height

    @staticmethod
    def simulate_mouse_activity(driver):
        # Move mouse to random positions
        action = webdriver.ActionChains(driver)
        for _ in range(3):
            x = random.randint(0, 500)
            y = random.randint(0, 500)
            try:
                action.move_by_offset(x, y).perform()
                action.move_by_offset(-x, -y).perform()
                time.sleep(random.uniform(0.1, 0.5))
            except:
                pass

class BharatFintechScraper:
    def __init__(self, local_mode=False):
        self.site_name = 'Bharat Fintech Summit'
        self.base_url = 'https://bharatfintechsummit.com/speakers/'
        self.local_mode = local_mode
        
        # Setup data directory
        self.data_dir = os.path.join(os.path.dirname(__file__), 'ScrapedData', 'BharatFintech')
        os.makedirs(self.data_dir, exist_ok=True)
        self.output_file = os.path.join(self.data_dir, 'bharat_fintech_speakers.csv')
        self.debug_file = os.path.join(os.path.dirname(__file__), 'bharat_debug.html')
        
        self.driver = None
        self.ua = UserAgent()

    def setup_driver(self):
        chrome_options = Options()
        # chrome_options.add_argument("--headless") # Comment out if you want to see the browser
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=" + StealthConfig.get_random_resolution())
        chrome_options.add_argument(f"user-agent={self.ua.random}")
        chrome_options.add_argument(f"--lang={StealthConfig.get_random_language()}")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        
        # Use existing ChromeDriver if available or let selenium find it
        self.driver = webdriver.Chrome(options=chrome_options)
        
        # Inject stealth scripts
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
            Object.defineProperty(navigator, 'webdriver', {
              get: () => undefined
            })
            """
        })
        
        self.driver.set_page_load_timeout(300)
        self.driver.implicitly_wait(10)

    def extract_speaker_data(self, soup):
        """Extract data from a speaker element/soup fragment"""
        try:
            # Name
            name = "N/A"
            name_elem = soup.find(['h2', 'h3', 'h4'], class_='elementor-heading-title')
            if name_elem:
                name = name_elem.get_text(strip=True)

            # Role & Company
            role = "N/A"
            company = "N/A"
            p_elems = soup.find_all('p', class_='elementor-heading-title')
            if len(p_elems) >= 1:
                role = p_elems[0].get_text(strip=True)
            if len(p_elems) >= 2:
                company = p_elems[1].get_text(strip=True)

            # Bio - searching across p tags primarily for better precision
            bio = "N/A"
            candidate_text = []
            
            # Find all p elements - usually contains the actual bio text without the extra card clutter
            for p in soup.find_all('p'):
                text = p.get_text(strip=True)
                if len(text) > 40:
                    candidate_text.append(text)
            
            if candidate_text:
                # The bio is usually the longest p tag that isn't name/role/company
                candidate_text.sort(key=len, reverse=True)
                for candidate in candidate_text:
                    if candidate != name and candidate != role and candidate != company:
                        # Ensure it's not just a collection of meta-data
                        if len(candidate) > 50:
                            bio = re.sub(r'\s+', ' ', candidate)
                            break

            # LinkedIn Search
            linkedin = ""
            # Look for any link containing linkedin.com
            social_link = soup.find('a', href=re.compile(r'linkedin\.com'))
            if social_link:
                linkedin = social_link.get('href', '')
            
            return {
                'Name': name,
                'Role/Designation': role,
                'Company': company,
                'Bio': bio,
                'Email ID': "Not Public",
                'LinkedIn': linkedin,
                'Twitter': "",
                'Facebook': "",
                'Source URL': self.base_url
            }
        except Exception as e:
            print(f"Error extracting speaker: {e}")
            return None

    def scrape(self):
        print(f"\n{'='*70}")
        print(f"  {self.site_name} Scraper")
        print(f"{'='*70}\n")
        
        try:
            if self.local_mode:
                print(f"Reading from local file: {self.debug_file}")
                with open(self.debug_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                soup = BeautifulSoup(content, 'html.parser')
            else:
                self.setup_driver()
                print(f"Loading {self.base_url}...")
                self.driver.get(self.base_url)
                
                # Human-like delay
                HumanBehavior.random_delay(5, 10)
                
                # Scroll to ensure all content (infinite scroll)
                print("Scrolling to load all speakers...")
                HumanBehavior.human_scroll(self.driver)
                
                # Get the final source
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                
                # Save for debugging
                with open(self.debug_file, 'w', encoding='utf-8') as f:
                    f.write(self.driver.page_source)
            
            # Find all speaker items
            # Based on analysis, they are in div[data-elementor-type="loop-item"]
            speakers = []
            loop_items = soup.find_all('div', {'data-elementor-type': 'loop-item'})
            
            print(f"Found {len(loop_items)} potential speaker items")
            
            processed_names = set()
            for i, item in enumerate(loop_items):
                # Each loop item has a main card and an off-canvas modal
                # We can extract most info from either, but bio is in the modal
                data = self.extract_speaker_data(item)
                if data and data['Name'] != "N/A" and data['Name'] not in processed_names:
                    print(f"[{i+1}] Processed: {data['Name']}")
                    speakers.append(data)
                    processed_names.add(data['Name'])
            
            # Save to CSV
            keys = ['Name', 'Role/Designation', 'Company', 'Bio', 'Email ID', 'LinkedIn', 'Twitter', 'Facebook', 'Source URL']
            with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=keys, quoting=csv.QUOTE_ALL)
                writer.writeheader()
                writer.writerows(speakers)
            
            print(f"\n✓ Successfully saved {len(speakers)} speakers to {self.output_file}")
            return speakers
            
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            if self.driver:
                self.driver.quit()

def main():
    parser = argparse.ArgumentParser(description='Bharat Fintech Summit Scraper')
    parser.add_argument('--local', action='store_true', help='Use local bharat_debug.html')
    args = parser.parse_args()
    
    scraper = BharatFintechScraper(local_mode=args.local)
    return scraper.scrape()

if __name__ == "__main__":
    main()
