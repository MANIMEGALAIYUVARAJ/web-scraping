"""
Advanced Gartner Scraper with Anti-Detection Features
Windows-compatible version without problematic dependencies
"""

import time
import re
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import csv
import os


class StealthConfig:
    """Configuration for anti-detection measures"""
    
    # User agent rotation
    try:
        ua = UserAgent()
    except:
        ua = None
    
    # Realistic screen resolutions
    SCREEN_RESOLUTIONS = [
        (1920, 1080), (1366, 768), (1536, 864), (1440, 900),
        (1280, 720), (1600, 900), (2560, 1440)
    ]
    
    # Languages
    LANGUAGES = [
        'en-US,en;q=0.9',
        'en-GB,en;q=0.9',
        'en-US,en;q=0.9,es;q=0.8'
    ]
    
    @staticmethod
    def get_random_user_agent():
        if StealthConfig.ua:
            try:
                return StealthConfig.ua.random
            except:
                pass
        # Fallback user agents
        fallback_uas = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
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
        """Random delay between actions"""
        time.sleep(random.uniform(min_sec, max_sec))
    
    @staticmethod
    def simulate_mouse_activity(driver):
        """Simulate mouse activity using JavaScript"""
        try:
            driver.execute_script("""
                // Simulate mouse movement
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
        """Scroll like a human with variable speed"""
        try:
            # Get scroll height
            last_height = driver.execute_script("return document.body.scrollHeight")
            
            # Scroll in chunks
            current_position = 0
            scroll_increment = random.randint(300, 600)
            
            while current_position < last_height:
                current_position += scroll_increment
                driver.execute_script(f"window.scrollTo({{top: {current_position}, behavior: 'smooth'}});")
                time.sleep(random.uniform(0.5, 1.5))
                
                # Random chance to scroll back up a bit (like reading)
                if random.random() < 0.3:
                    back_scroll = random.randint(50, 200)
                    current_position -= back_scroll
                    driver.execute_script(f"window.scrollTo({{top: {current_position}, behavior: 'smooth'}});")
                    time.sleep(random.uniform(0.3, 0.8))
                
                # Update last_height in case of lazy loading
                last_height = driver.execute_script("return document.body.scrollHeight")
        except Exception as e:
            print(f"    Scroll error: {e}")


class GartnerScraperAdvanced:
    def __init__(self):
        self.region = 'UK'
        self.site_name = 'Gartner CFO Finance'
        self.base_url = 'https://www.gartner.com/en/conferences/emea/cfo-finance-uk/speakers'
        
        # Setup data directory
        self.data_dir = os.path.join(os.path.dirname(__file__), 'ScrapedData', self.region)
        os.makedirs(self.data_dir, exist_ok=True)
        self.output_file = os.path.join(self.data_dir, 'gartner_cfo_finance_advanced.csv')
        
        # Setup Selenium
        self.driver = None
        self.stealth_config = StealthConfig()
        
    def setup_driver(self):
        """Initialize undetected ChromeDriver with advanced stealth"""
        print("Setting up advanced stealth browser...")
        
        try:
            options = uc.ChromeOptions()
            
            # Get random configuration
            width, height = self.stealth_config.get_random_resolution()
            user_agent = self.stealth_config.get_random_user_agent()
            language = self.stealth_config.get_random_language()
            
            # Advanced stealth settings
            options.add_argument(f'--window-size={width},{height}')
            options.add_argument(f'--user-agent={user_agent}')
            options.add_argument(f'--lang={language.split(",")[0]}')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-sandbox')
            
            # Additional fingerprint randomization
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_experimental_option("prefs", {
                "profile.default_content_setting_values.notifications": 2,
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False
            })
            
            # Use undetected chromedriver
            print("Initializing ChromeDriver...")
            self.driver = uc.Chrome(options=options, version_main=None)
            
            # Override navigator properties
            self.inject_stealth_js()
            
            self.driver.implicitly_wait(10)
            
            print(f"✓ Browser configured: {width}x{height}")
            print(f"✓ User Agent: {user_agent[:80]}...")
            
        except Exception as e:
            print(f"Error setting up driver: {e}")
            raise
        
    def inject_stealth_js(self):
        """Inject JavaScript to override detection points"""
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
        except Exception as e:
            print(f"Warning: Could not inject stealth JS: {e}")
    
    def wait_for_cloudflare(self, max_wait=30):
        """Wait for Cloudflare challenge to complete"""
        print("Checking for Cloudflare challenge...")
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                page_title = self.driver.title
                page_source = self.driver.page_source.lower()
                
                # Check if Cloudflare is present
                if "just a moment" in page_title.lower() or "cloudflare" in page_source[:5000]:
                    elapsed = int(time.time() - start_time)
                    print(f"  Cloudflare detected, waiting... ({elapsed}s)")
                    HumanBehavior.random_delay(2, 4)
                else:
                    print("  ✓ Cloudflare challenge passed!")
                    return True
            except:
                pass
        
        print("  ⚠ Cloudflare wait timeout")
        return False
    
    def extract_event_info(self, soup):
        """Extract event date and location"""
        date_place = ""
        try:
            date_elem = soup.find('div', class_='nav-conf-date')
            if date_elem:
                date_place = date_elem.get_text(strip=True)
                
            location_elem = soup.find('div', class_='nav-conf-location')
            if location_elem:
                location_text = location_elem.get_text(strip=True)
                if date_place:
                    date_place += f"\n{location_text}"
                else:
                    date_place = location_text
        except:
            date_place = "8 – 9 June 2026\nLondon, U.K."
            
        return date_place
    
    def extract_speaker_details(self, detail_url, save_debug=False):
        """Visit a speaker's detail page and extract bio, topics, and sessions"""
        try:
            print(f"    Fetching details from: {detail_url}")
            
            # Human-like navigation
            HumanBehavior.random_delay(3, 6)
            self.driver.get(detail_url)
            
            # Wait for Cloudflare
            self.wait_for_cloudflare(max_wait=20)
            
            # Additional wait for page to fully load
            HumanBehavior.random_delay(2, 4)
            
            # Simulate human behavior
            HumanBehavior.simulate_mouse_activity(self.driver)
            HumanBehavior.human_scroll(self.driver)
            
            detail_soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Save debug HTML for first speaker
            if save_debug:
                debug_file = os.path.join(self.data_dir, 'speaker_detail_debug.html')
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(self.driver.page_source)
                print(f"    💾 Saved detail page HTML to: {debug_file}")
            
            # Extract bio with multiple fallback selectors
            bio = "N/A"
            bio_selectors = [
                ('div', 'speaker-bio'),
                ('div', 'bio'),
                ('div', 'biography'),
                ('section', 'speaker-bio'),
                ('div', {'class': re.compile(r'.*bio.*', re.I)}),
                ('p', {'class': re.compile(r'.*bio.*', re.I)})
            ]
            
            for tag, attrs in bio_selectors:
                bio_section = detail_soup.find(tag, attrs)
                if bio_section:
                    bio_text = bio_section.get_text(separator=' ', strip=True)
                    bio_text = re.sub(r'Show More|Show Less|Read More|Read Less', '', bio_text).strip()
                    if bio_text and len(bio_text) > 20:
                        bio = bio_text
                        print(f"    ✓ Bio found using: {tag}.{attrs}")
                        break
            
            # Extract topics with multiple fallback selectors
            topics = []
            topic_selectors = [
                ('div', 'speaker-topics'),
                ('ul', 'topics'),
                ('div', 'topics'),
                ('div', {'class': re.compile(r'.*topic.*', re.I)}),
                ('ul', {'class': re.compile(r'.*tag.*', re.I)})
            ]
            
            for tag, attrs in topic_selectors:
                topic_section = detail_soup.find(tag, attrs)
                if topic_section:
                    topic_items = topic_section.find_all('li')
                    if not topic_items:
                        topic_items = topic_section.find_all(['span', 'div', 'a'])
                    
                    for item in topic_items:
                        topic_text = item.get_text(strip=True)
                        if topic_text and len(topic_text) > 2:
                            topics.append(topic_text)
                    
                    if topics:
                        print(f"    ✓ Topics found using: {tag}.{attrs}")
                        break
            
            topics_str = ', '.join(topics) if topics else "N/A"
            
            # Extract sessions with multiple fallback selectors
            sessions = []
            session_selectors = [
                ('div', 'session'),
                ('div', 'session-item'),
                ('div', 'session-card'),
                ('article', 'session'),
                ('div', {'class': re.compile(r'.*session.*', re.I)}),
                ('div', {'class': re.compile(r'.*agenda.*', re.I)})
            ]
            
            for tag, attrs in session_selectors:
                session_divs = detail_soup.find_all(tag, attrs)
                if session_divs:
                    for session_div in session_divs:
                        session_data = {}
                        
                        # Session title
                        title_elem = (session_div.find('h3') or 
                                    session_div.find('h4') or 
                                    session_div.find('h2') or
                                    session_div.find('a', class_=re.compile(r'.*title.*', re.I)))
                        if title_elem:
                            session_data['title'] = title_elem.get_text(strip=True)
                        
                        # Session time/date
                        time_elem = (session_div.find('div', class_=re.compile(r'.*time.*', re.I)) or
                                   session_div.find('span', class_=re.compile(r'.*time.*', re.I)) or
                                   session_div.find('div', class_=re.compile(r'.*date.*', re.I)))
                        if time_elem:
                            session_data['time'] = time_elem.get_text(strip=True)
                        
                        # Session description
                        desc_elem = (session_div.find('div', class_=re.compile(r'.*desc.*', re.I)) or
                                   session_div.find('p'))
                        if desc_elem:
                            session_data['description'] = desc_elem.get_text(strip=True)
                        
                        if session_data:
                            sessions.append(session_data)
                    
                    if sessions:
                        print(f"    ✓ Sessions found using: {tag}.{attrs}")
                        break
            
            # Format sessions as text
            sessions_str = ""
            for i, session in enumerate(sessions, 1):
                sessions_str += f"\n\nSession {i}:\n"
                if 'title' in session:
                    sessions_str += f"Title: {session['title']}\n"
                if 'time' in session:
                    sessions_str += f"Time: {session['time']}\n"
                if 'description' in session:
                    sessions_str += f"Description: {session['description']}\n"
            sessions_str = sessions_str.strip() if sessions_str else "N/A"
            
            return {
                'bio': bio,
                'topics': topics_str,
                'sessions': sessions_str
            }
            
        except Exception as e:
            print(f"    ❌ Error fetching speaker details: {e}")
            return {
                'bio': "N/A",
                'topics': "N/A",
                'sessions': "N/A"
            }
    
    def extract_speaker_data(self, speaker_elem, event_date_place, save_debug=False):
        """Extract all data for a single speaker"""
        try:
            soup = BeautifulSoup(str(speaker_elem), 'html.parser')
            
            # Extract Name
            name = "N/A"
            name_elem = soup.find('h3', class_='speaker-name')
            if name_elem:
                name = name_elem.get_text(strip=True)
            
            if name == "N/A" or len(name) < 3:
                return None
            
            # Extract Role/Designation
            role = "N/A"
            role_elem = soup.find('div', class_='jobTitle')
            if role_elem:
                role = role_elem.get_text(strip=True)
            
            # Extract Company
            company = "N/A"
            company_elem = soup.find('div', class_='company')
            if company_elem:
                company = company_elem.get_text(strip=True)
                if company != "N/A" and role != "N/A":
                    role = f"{role}, {company}"
            
            # Get speaker detail page URL
            detail_url = None
            if speaker_elem.name == 'a' and speaker_elem.get('href'):
                href = speaker_elem.get('href')
                detail_url = href if href.startswith('http') else f"https://www.gartner.com{href}"
            
            # Fetch detailed information from speaker's page
            if detail_url:
                details = self.extract_speaker_details(detail_url, save_debug)
                topics_str = details['topics']
                bio = details['bio']
                sessions_str = details['sessions']
            else:
                topics_str = "N/A"
                bio = "N/A"
                sessions_str = "N/A"
            
            # Extract social media links
            social = {
                'YouTube': '',
                'Twitter': '',
                'LinkedIn': '',
                'Facebook': '',
                'Instagram': ''
            }
            
            social_links = soup.find_all('a', class_='social-link')
            for link in social_links:
                href = link.get('href', '')
                if 'youtube.com' in href or 'youtu.be' in href:
                    social['YouTube'] = href
                elif 'twitter.com' in href or 'x.com' in href:
                    social['Twitter'] = href
                elif 'linkedin.com' in href:
                    social['LinkedIn'] = href
                elif 'facebook.com' in href:
                    social['Facebook'] = href
                elif 'instagram.com' in href:
                    social['Instagram'] = href
            
            # Extract email
            email = "Not Public"
            email_link = soup.find('a', href=re.compile(r'^mailto:'))
            if email_link:
                email = email_link['href'].replace('mailto:', '').split('?')[0]
            
            return {
                'Name': name,
                'Date and Place': event_date_place,
                'Role/Designation': role,
                'Speaker Topics': topics_str,
                'Speaker Bio': bio,
                'Sessions': sessions_str,
                'Email ID': email,
                'YouTube': social['YouTube'],
                'Twitter': social['Twitter'],
                'LinkedIn': social['LinkedIn'],
                'Facebook': social['Facebook'],
                'Instagram': social['Instagram'],
                'Source URL': self.base_url
            }
            
        except Exception as e:
            print(f"Error extracting speaker data: {e}")
            return None
    
    def scrape(self):
        """Main scraping function"""
        print(f"\n{'='*70}")
        print(f"  {self.site_name} Advanced Scraper")
        print(f"{'='*70}\n")
        
        try:
            self.setup_driver()
            print("\nLoading main speakers page...")
            self.driver.get(self.base_url)
            
            # Wait for Cloudflare
            self.wait_for_cloudflare()
            
            # Human-like behavior
            HumanBehavior.random_delay(3, 5)
            HumanBehavior.simulate_mouse_activity(self.driver)
            
            # Scroll to load all speakers
            print("Scrolling to load all content...")
            HumanBehavior.human_scroll(self.driver)
            
            # Get page source
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Extract event date and place
            event_date_place = self.extract_event_info(soup)
            print(f"Event: {event_date_place}")
            
            # Find all speaker elements
            speaker_containers = soup.find_all('a', class_='speaker-block')
            
            print(f"\n{'='*70}")
            print(f"Found {len(speaker_containers)} speaker elements")
            print(f"{'='*70}\n")
            
            results = []
            processed_names = set()
            first_speaker = True
            
            for i, speaker_elem in enumerate(speaker_containers, 1):
                print(f"\n[{i}/{len(speaker_containers)}] Processing speaker...")
                
                speaker_data = self.extract_speaker_data(speaker_elem, event_date_place, first_speaker)
                first_speaker = False
                
                if speaker_data and speaker_data['Name'] != "N/A":
                    if speaker_data['Name'] not in processed_names:
                        results.append(speaker_data)
                        processed_names.add(speaker_data['Name'])
                        print(f"  ✓ {speaker_data['Name']}")
                        if speaker_data['Speaker Bio'] != "N/A":
                            print(f"    Bio: {speaker_data['Speaker Bio'][:60]}...")
                        if speaker_data['Speaker Topics'] != "N/A":
                            print(f"    Topics: {speaker_data['Speaker Topics'][:60]}...")
                    else:
                        print(f"  ⊘ Skipping duplicate: {speaker_data['Name']}")
            
            # Save to CSV
            if results:
                self.save_to_csv(results)
                print(f"\n{'='*70}")
                print(f"✓ Successfully scraped {len(results)} speakers")
                print(f"✓ Data saved to: {self.output_file}")
                
                # Print summary
                bio_count = sum(1 for r in results if r['Speaker Bio'] != "N/A")
                topics_count = sum(1 for r in results if r['Speaker Topics'] != "N/A")
                sessions_count = sum(1 for r in results if r['Sessions'] != "N/A")
                
                print(f"\nData Quality Summary:")
                print(f"  📝 Bios extracted: {bio_count}/{len(results)} ({bio_count*100//len(results)}%)")
                print(f"  🏷️  Topics extracted: {topics_count}/{len(results)} ({topics_count*100//len(results)}%)")
                print(f"  📅 Sessions extracted: {sessions_count}/{len(results)} ({sessions_count*100//len(results)}%)")
                print(f"{'='*70}\n")
            else:
                print("\n✗ No speakers found")
                
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
        keys = ['Name', 'Date and Place', 'Role/Designation', 'Speaker Topics', 'Speaker Bio', 
                'Sessions', 'Email ID', 'YouTube', 'Twitter', 'LinkedIn', 'Facebook', 'Instagram', 'Source URL']
        
        with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            writer.writerows(data)


def main():
    scraper = GartnerScraperAdvanced()
    scraper.scrape()


if __name__ == "__main__":
    main()
