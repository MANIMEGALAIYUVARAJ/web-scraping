"""
NexGen Banking Scraper - Advanced Anti-Detection
Template scraper ready to be customized once website structure is known
"""

import time
import re
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import csv
import os
import sys
import argparse


class StealthConfig:
    """Configuration for anti-detection measures"""
    
    try:
        ua = UserAgent()
    except:
        ua = None
    
    SCREEN_RESOLUTIONS = [
        (1920, 1080), (1366, 768), (1536, 864), (1440, 900),
        (1280, 720), (1600, 900), (2560, 1440)
    ]
    
    LANGUAGES = ['en-US,en;q=0.9', 'en-GB,en;q=0.9']
    
    @staticmethod
    def get_random_user_agent():
        if StealthConfig.ua:
            try:
                return StealthConfig.ua.random
            except:
                pass
        fallback_uas = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        ]
        return random.choice(fallback_uas)
    
    @staticmethod
    def get_random_resolution():
        return random.choice(StealthConfig.SCREEN_RESOLUTIONS)
    
    @staticmethod
    def get_random_language():
        return random.choice(StealthConfig.LANGUAGES)


class HumanBehavior:
    """Simulate human-like behavior"""
    
    @staticmethod
    def random_delay(min_sec=2, max_sec=5):
        time.sleep(random.uniform(min_sec, max_sec))
    
    @staticmethod
    def simulate_mouse_activity(driver):
        try:
            driver.execute_script("""
                for (let i = 0; i < 3; i++) {
                    var event = new MouseEvent('mousemove', {
                        'view': window,
                        'bubbles': true,
                        'cancelable': true,
                        'clientX': Math.random() * window.innerWidth,
                        'clientY': Math.random() * window.innerHeight
                    });
                    document.dispatchEvent(event);
                }
            """)
        except:
            pass
    
    @staticmethod
    def human_scroll(driver):
        try:
            last_height = driver.execute_script("return document.body.scrollHeight")
            current_position = 0
            scroll_increment = random.randint(300, 600)
            
            while current_position < last_height:
                current_position += scroll_increment
                driver.execute_script(f"window.scrollTo({{top: {current_position}, behavior: 'smooth'}});")
                time.sleep(random.uniform(0.5, 1.5))
                
                if random.random() < 0.3:
                    back_scroll = random.randint(50, 200)
                    current_position -= back_scroll
                    driver.execute_script(f"window.scrollTo({{top: {current_position}, behavior: 'smooth'}});")
                    time.sleep(random.uniform(0.3, 0.8))
                
                last_height = driver.execute_script("return document.body.scrollHeight")
        except Exception as e:
            print(f"    Scroll error: {e}")


class NexGenBankingScraper:
    def __init__(self, local_mode=False):
        self.site_name = 'NexGen Banking'
        self.base_url = 'https://nexgenbanking.com'
        self.local_mode = local_mode
        
        # Setup data directory
        self.data_dir = os.path.join(os.path.dirname(__file__), 'ScrapedData', 'NexGen')
        os.makedirs(self.data_dir, exist_ok=True)
        self.output_file = os.path.join(self.data_dir, 'nexgen_banking_speakers.csv')
        self.debug_file = os.path.join(self.data_dir, 'page_debug.html')
        
        self.driver = None
        self.stealth_config = StealthConfig()
        
    def setup_driver(self):
        """Initialize Chrome WebDriver with stealth settings"""
        print("Setting up stealth browser...")
        
        try:
            options = Options()
            
            width, height = self.stealth_config.get_random_resolution()
            user_agent = self.stealth_config.get_random_user_agent()
            language = self.stealth_config.get_random_language()
            
            # Stealth arguments
            options.add_argument(f'--window-size={width},{height}')
            options.add_argument(f'--user-agent={user_agent}')
            options.add_argument(f'--lang={language.split(",")[0]}')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-sandbox')
            options.add_argument('--start-maximized')
            
            # Experimental options
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_experimental_option("prefs", {
                "profile.default_content_setting_values.notifications": 2,
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False
            })
            
            print("Initializing ChromeDriver...")
            self.driver = webdriver.Chrome(options=options)
            
            # Set timeouts - increased for robustness
            self.driver.set_page_load_timeout(300)
            self.driver.set_script_timeout(120)
            self.driver.implicitly_wait(20)
            
            # Inject stealth JavaScript
            try:
                stealth_js = """
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
                window.chrome = {runtime: {}};
                """
                
                self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                    'source': stealth_js
                })
                print("✓ Stealth JavaScript injected")
            except Exception as e:
                print(f"⚠ Could not inject stealth JS: {e}")
            
            self.driver.implicitly_wait(15)
            
            print(f"✓ Browser configured: {width}x{height}")
            print(f"✓ User Agent: {user_agent[:80]}...")
            
        except Exception as e:
            print(f"Error setting up driver: {e}")
            raise
    
    def extract_speaker_data(self, speaker_elem):
        """
        Extract data from a speaker element using identified selectors
        """
        try:
            # speaker_elem is already a BeautifulSoup object or can be converted
            soup = speaker_elem if hasattr(speaker_elem, 'find') else BeautifulSoup(str(speaker_elem), 'html.parser')
            
            # Name is in <h4>
            name = "N/A"
            name_elem = soup.find('h4')
            if name_elem:
                name = name_elem.get_text(strip=True)
            
            # Role/Designation is in <p class="profile-text">
            role = "N/A"
            role_elem = soup.find('p', class_='profile-text')
            if role_elem:
                role = role_elem.get_text(strip=True)
            
            # Company is in <p class="group-text">
            company = "N/A"
            company_elem = soup.find('p', class_='group-text')
            if company_elem:
                company = company_elem.get_text(strip=True)
            
            # Bio is not immediately visible in the card, but let's check for title attribute or similar
            # For now, we'll keep it as N/A as it's not in the identified card structure
            bio = "N/A"
            
            # Email is not public in these cards
            email = "Not Public"
            
            # Extract LinkedIn from the parent <a> tag if speaker_elem is the <a> or contains it
            linkedin = "N/A"
            href = ""
            if speaker_elem.name == 'a':
                href = speaker_elem.get('href', '')
            else:
                social_link = soup.find('a', href=re.compile(r'linkedin\.com'))
                if social_link:
                    href = social_link.get('href', '')
            
            # Verify it's a LinkedIn URL
            if 'linkedin.com' in href:
                linkedin = href
            
            return {
                'Name': name,
                'Role/Designation': role,
                'Company': company,
                'Bio': bio,
                'Email ID': email,
                'LinkedIn': linkedin,
                'Twitter': "",
                'Facebook': "",
                'Source URL': self.base_url
            }
            
        except Exception as e:
            print(f"    Error extracting speaker data: {e}")
            return None
    
    def scrape(self, query=None, limit=10):
        """Main scraping function with query and limit support"""
        print(f"\n{'='*70}")
        print(f"  {self.site_name} Scraper (Advanced Anti-Detection)")
        print(f"{'='*70}\n")
        
        try:
            if self.local_mode:
                print("\n[Local Mode] Reading data from existing debug file...")
                if os.path.exists(self.debug_file):
                    with open(self.debug_file, 'r', encoding='utf-8') as f:
                        page_source = f.read()
                    soup = BeautifulSoup(page_source, 'html.parser')
                else:
                    print(f"❌ Debug file not found at {self.debug_file}")
                    return
            else:
                self.setup_driver()
                
                # Load page with retry logic
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        print(f"\nLoading {self.base_url}... (Attempt {attempt + 1}/{max_retries})")
                        self.driver.get(self.base_url)
                        
                        print("Waiting for page to fully load...")
                        HumanBehavior.random_delay(5, 8)
                        
                        if self.driver.title:
                            print(f"✓ Page loaded: {self.driver.title}")
                            break
                            
                    except Exception as e:
                        print(f"❌ Error on attempt {attempt + 1}: {e}")
                        if attempt < max_retries - 1:
                            wait_time = (attempt + 1) * 15
                            print(f"Waiting {wait_time} seconds before retry...")
                            time.sleep(wait_time)
                        else:
                            print("⚠ Website is not accessible. Attempting to use existing debug file as fallback...")
                            if os.path.exists(self.debug_file):
                                with open(self.debug_file, 'r', encoding='utf-8') as f:
                                    page_source = f.read()
                                soup = BeautifulSoup(page_source, 'html.parser')
                                break
                            raise Exception("Website is not accessible and no fallback debug file found")
                
                if not 'soup' in locals():
                    # Simulate human behavior
                    HumanBehavior.simulate_mouse_activity(self.driver)
                    
                    # Scroll to load all content
                    print("\nScrolling to load all content...")
                    HumanBehavior.human_scroll(self.driver)
                    
                    # Get page source
                    page_source = self.driver.page_source
                    soup = BeautifulSoup(page_source, 'html.parser')
                    
                    # Save HTML for analysis
                    with open(self.debug_file, 'w', encoding='utf-8') as f:
                        f.write(page_source)
                    print(f"✓ Saved page HTML to: {self.debug_file}")
            
            # Find the speaker section by ID
            speaker_section = soup.find(id='Speaker')
            if not speaker_section:
                print("\n⚠ Could not find section with id='Speaker'")
                # Fallback to general search if section not found
                speaker_containers = soup.find_all('p', class_='profile-text')
                if speaker_containers:
                    # If we found profile texts, the parents are likely the containers
                    speaker_containers = [p.find_parent('a') or p.find_parent('div') for p in speaker_containers]
            else:
                # Find all <a> tags within the speaker section that contain profile-text
                speaker_containers = []
                all_links = speaker_section.find_all('a')
                for link in all_links:
                    if link.find('p', class_='profile-text'):
                        speaker_containers.append(link)
            
            if not speaker_containers:
                print("\n⚠ No speaker elements found with identified selectors")
                return
            
            print(f"\n{'='*70}")
            print(f"Processing {len(speaker_containers)} speakers")
            print(f"{'='*70}\n")
            
            results = []
            processed_names = set()
            
            for i, speaker_elem in enumerate(speaker_containers, 1):
                if len(results) >= limit:
                    print(f"\n✓ Reached limit of {limit} results.")
                    break
                    
                print(f"\n[{i}/{len(speaker_containers)}] Processing speaker...")
                
                speaker_data = self.extract_speaker_data(speaker_elem)
                
                if speaker_data and speaker_data['Name'] != "N/A":
                    # Query filtering logic
                    if query:
                        search_content = f"{speaker_data['Name']} {speaker_data['Role/Designation']} {speaker_data['Company']}".lower()
                        if query.lower() not in search_content:
                            print(f"  - Skipping: Does not match query '{query}'")
                            continue

                    if speaker_data['Name'] not in processed_names:
                        results.append(speaker_data)
                        processed_names.add(speaker_data['Name'])
                        print(f"  ✓ {speaker_data['Name']} [{len(results)}/{limit}]")
                        if speaker_data['Role/Designation'] != "N/A":
                            print(f"    Role: {speaker_data['Role/Designation'][:60]}...")
                    else:
                        print(f"  ⊘ Skipping duplicate: {speaker_data['Name']}")
                
                # Delay between speakers
                HumanBehavior.random_delay(0.5, 1.5)
            
            # Save to CSV
            if results:
                self.save_to_csv(results)
                print(f"\n{'='*70}")
                print(f"✓ Successfully scraped {len(results)} speakers")
                print(f"✓ Data saved to: {self.output_file}")
                print(f"{'='*70}\n")
                return results
            else:
                print("\n✗ No speakers found")
                print("Check the debug HTML file to update selectors")
                
        except Exception as e:
            print(f"\n❌ Error during scraping: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.driver:
                print("\nClosing browser...")
                self.driver.quit()
                print("✓ Browser closed\n")
    
    def save_to_csv(self, data):
        """Save scraped data to CSV"""
        keys = ['Name', 'Role/Designation', 'Company', 'Bio', 'Email ID', 
                'LinkedIn', 'Twitter', 'Facebook', 'Source URL']
        
        with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            writer.writerows(data)


def main():
    parser = argparse.ArgumentParser(description='NexGen Banking Scraper')
    parser.add_argument('--local', action='store_true', help='Process existing page_debug.html instead of loading live site')
    parser.add_argument('--query', type=str, default=None, help='Search query to filter speakers')
    parser.add_argument('--limit', type=int, default=10, help='Maximum number of speakers to scrape')
    args = parser.parse_args()
    
    scraper = NexGenBankingScraper(local_mode=args.local)
    return scraper.scrape(query=args.query, limit=args.limit)


if __name__ == "__main__":
    main()
