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
    @staticmethod
    def get_random_resolution():
        resolutions = ["1920,1080", "1600,900", "1536,864", "1440,900", "1366,768"]
        return random.choice(resolutions)

    @staticmethod
    def get_random_language():
        languages = ["en-US,en;q=0.9", "en-GB,en;q=0.8", "en-CA,en;q=0.7"]
        return random.choice(languages)

class HumanBehavior:
    @staticmethod
    def random_delay(min_sec=2, max_sec=5):
        time.sleep(random.uniform(min_sec, max_sec))

    @staticmethod
    def human_scroll(driver):
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            scroll_step = random.randint(300, 700)
            current_pos = 0
            while current_pos < last_height:
                current_pos += scroll_step
                driver.execute_script(f"window.scrollTo(0, {current_pos});")
                time.sleep(random.uniform(0.1, 0.3))
            
            time.sleep(3)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(5)
                if driver.execute_script("return document.body.scrollHeight") == last_height:
                    break
            last_height = new_height

    @staticmethod
    def click_load_more(driver):
        """Click the 'Load More' button if it exists and is visible"""
        print("Starting 'Load More' sequence to reveal all industry speakers...")
        for batch in range(1, 20): # increased limit
            try:
                # Scroll to the very bottom to ensure button is triggered/loaded
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                
                # Try finding the specific Elementor "Load More" button structure
                load_more = None
                selectors = [
                    (By.CSS_SELECTOR, ".e-loop__load-more a"),
                    (By.XPATH, "//span[text()='Load More']/ancestor::a"),
                    (By.XPATH, "//div[contains(@class, 'e-loop__load-more')]//a"),
                    (By.CSS_SELECTOR, ".hspeaker2025_container #loadMore")
                ]
                
                for by, selector in selectors:
                    try:
                        btns = driver.find_elements(by, selector)
                        for btn in btns:
                            if btn.is_displayed():
                                load_more = btn
                                break
                        if load_more: break
                    except:
                        continue
                
                if load_more:
                    print(f"Found 'Load More' button. Clicking Batch {batch}...")
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", load_more)
                    time.sleep(1)
                    
                    # Ensure the button is actually clickable (not obscured)
                    try:
                        load_more.click()
                    except:
                        driver.execute_script("arguments[0].click();", load_more)
                    
                    # Longer wait for content injection
                    print(f"Batch {batch} clicked. Waiting for content refresh...")
                    time.sleep(8) 
                    
                    # Post-click scroll to avoid getting stuck
                    driver.execute_script("window.scrollBy(0, 400);")
                    time.sleep(2)
                else:
                    # Check if we really finished or just missed it
                    print(f"No more 'Load More' visible after Batch {batch-1}. Checking if end reached...")
                    # Small scroll up and down to be absolutely sure
                    driver.execute_script("window.scrollBy(0, -500);")
                    time.sleep(1)
                    driver.execute_script("window.scrollBy(0, 1000);")
                    time.sleep(2)
                    
                    # Try one last check
                    try:
                        if not driver.find_element(By.CSS_SELECTOR, ".e-loop__load-more a").is_displayed():
                            print("Confirmed: All speakers revealed.")
                            break
                    except:
                        print("Confirmed: Load More button disappeared.")
                        break
            except Exception as e:
                print(f"Non-critical error in Load More loop: {e}")
                break
        print("Load More sequence complete.")

class Bharat2025Scraper:
    def __init__(self, local_mode=False):
        self.site_name = 'Bharat Fintech Summit 2025'
        self.base_url = 'https://bharatfintechsummit.com/bfs-2025/'
        self.local_mode = local_mode
        
        # Setup data directory
        self.data_dir = os.path.join(os.path.dirname(__file__), 'ScrapedData', 'BharatFintech2025')
        os.makedirs(self.data_dir, exist_ok=True)
        self.output_file = os.path.join(self.data_dir, 'bharat_2025_FULL_230_speakers.csv')
        self.debug_file = os.path.join(os.path.dirname(__file__), 'bharat_2025_debug.html')
        
        self.driver = None
        self.ua = UserAgent()

    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=" + StealthConfig.get_random_resolution())
        chrome_options.add_argument(f"user-agent={self.ua.random}")
        chrome_options.add_argument(f"--lang={StealthConfig.get_random_language()}")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })
        self.driver.set_page_load_timeout(300)
        self.driver.implicitly_wait(10)

    def extract_speaker_data(self, item_soup, full_soup):
        """Extract data from a loop item and its associated modal"""
        try:
            # Basic info from the visible card
            name = "N/A"
            name_elem = item_soup.find(['h2', 'h3', 'h4'], class_='elementor-heading-title')
            if name_elem:
                name = name_elem.get_text(strip=True)

            role = "N/A"
            company = "N/A"
            p_elems = item_soup.find_all('p', class_='elementor-heading-title')
            if len(p_elems) >= 1:
                role = p_elems[0].get_text(strip=True)
            if len(p_elems) >= 2:
                company = p_elems[1].get_text(strip=True)

            # Find the modal ID from the "About" link
            modal_id = ""
            about_link = item_soup.find('a', class_='eae-popup-link')
            if about_link:
                modal_id = about_link.get('href', '').replace('#', '')

            bio = "N/A"
            linkedin = ""

            # If we have a modal ID, look it up in the full soup
            if modal_id:
                modal_div = full_soup.find('div', id=modal_id)
                if modal_div:
                    # LinkedIn in modal
                    li_link = modal_div.find('a', href=re.compile(r'linkedin\.com'))
                    if li_link:
                        linkedin = li_link.get('href', '')
                    
                    # Bio in modal - usually in elementor-widget-text-editor
                    bio_elem = modal_div.find('div', class_='elementor-widget-text-editor')
                    if bio_elem:
                        bio = bio_elem.get_text(separator=' ', strip=True)
                        bio = re.sub(r'\s+', ' ', bio)

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
            if self.local_mode and os.path.exists(self.debug_file):
                print(f"Reading from local file: {self.debug_file}")
                with open(self.debug_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                soup = BeautifulSoup(content, 'html.parser')
            else:
                self.setup_driver()
                print(f"Loading {self.base_url}...")
                self.driver.get(self.base_url)
                HumanBehavior.random_delay(5, 10)
                
                print("Scrolling page...")
                HumanBehavior.human_scroll(self.driver)
                
                # Specifically handle the "Load More" button for 2025
                HumanBehavior.click_load_more(self.driver)
                
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                with open(self.debug_file, 'w', encoding='utf-8') as f:
                    f.write(self.driver.page_source)
            
            # Find all speaker items
            speakers = []
            loop_items = soup.find_all('div', {'data-elementor-type': 'loop-item'})
            
            print(f"Found {len(loop_items)} potential speaker items")
            
            processed_names = set()
            for i, item in enumerate(loop_items):
                data = self.extract_speaker_data(item, soup)
                if data and data['Name'] != "N/A" and data['Name'] not in processed_names:
                    print(f"[#] {len(speakers)+1}: {data['Name']} ({data['Role/Designation']} @ {data['Company']})")
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
    parser = argparse.ArgumentParser(description='Bharat Fintech Summit 2025 Scraper')
    parser.add_argument('--local', action='store_true', help='Use local debug HTML')
    args = parser.parse_args()
    
    scraper = Bharat2025Scraper(local_mode=args.local)
    return scraper.scrape()

if __name__ == "__main__":
    main()
