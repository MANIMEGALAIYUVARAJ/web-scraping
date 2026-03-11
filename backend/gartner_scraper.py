import time
import re
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import csv
import os

class GartnerScraper:
    def __init__(self):
        self.region = 'UK'
        self.site_name = 'Gartner CFO Finance'
        self.base_url = 'https://www.gartner.com/en/conferences/emea/cfo-finance-uk/speakers'
        
        # Setup data directory
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', 'ScrapedData', self.region)
        os.makedirs(self.data_dir, exist_ok=True)
        self.output_file = os.path.join(self.data_dir, 'gartner_cfo_finance.csv')
        
        # Setup Selenium
        self.driver = None
        
    def setup_driver(self):
        """Initialize undetected ChromeDriver to bypass Cloudflare"""
        options = uc.ChromeOptions()
        
        # Stealth settings
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--start-maximized')
        
        # Use undetected chromedriver
        self.driver = uc.Chrome(options=options, version_main=None)
        self.driver.implicitly_wait(15)
        
    def extract_event_info(self, soup):
        """Extract event date and location"""
        date_place = ""
        try:
            # Look for date in nav-conf-date class
            date_elem = soup.find('div', class_='nav-conf-date')
            if date_elem:
                date_text = date_elem.get_text(strip=True)
                date_place = date_text
                
            # Look for location
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
    
    def extract_social_links(self, soup):
        """Extract social media links"""
        social = {
            'YouTube': '',
            'Twitter': '',
            'LinkedIn': '',
            'Facebook': '',
            'Instagram': ''
        }
        
        try:
            # Find all social links
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
        except Exception as e:
            print(f"Error extracting social links: {e}")
            
        return social
    
    def extract_speaker_details(self, detail_url, save_debug=False):
        """Visit a speaker's detail page and extract bio, topics, and sessions"""
        try:
            print(f"    Fetching details from: {detail_url}")
            self.driver.get(detail_url)
            
            # Wait longer for Cloudflare challenge to complete
            print(f"    Waiting for Cloudflare challenge...")
            time.sleep(8)  # Give Cloudflare time to verify
            
            # Check if we're still on Cloudflare page
            page_title = self.driver.title
            if "Just a moment" in page_title or "Gartner.com" == page_title:
                print(f"    Cloudflare detected, waiting additional time...")
                time.sleep(10)  # Wait even longer
            
            detail_soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Save debug HTML for first speaker
            if save_debug:
                debug_file = os.path.join(self.data_dir, 'speaker_detail_debug.html')
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(self.driver.page_source)
                print(f"    Saved detail page HTML to: {debug_file}")
            
            # Extract bio
            bio = "N/A"
            bio_section = detail_soup.find('div', class_='speaker-bio') or detail_soup.find('div', class_='bio')
            if bio_section:
                bio_text = bio_section.get_text(separator=' ', strip=True)
                bio_text = re.sub(r'Show More|Show Less', '', bio_text).strip()
                if bio_text:
                    bio = bio_text
            
            # Extract topics
            topics = []
            topic_section = detail_soup.find('div', class_='speaker-topics') or detail_soup.find('ul', class_='topics')
            if topic_section:
                topic_items = topic_section.find_all('li')
                for item in topic_items:
                    topic_text = item.get_text(strip=True)
                    if topic_text and len(topic_text) > 2:
                        topics.append(topic_text)
            topics_str = ', '.join(topics) if topics else "N/A"
            
            # Extract sessions
            sessions = []
            session_divs = detail_soup.find_all('div', class_='session') or detail_soup.find_all('div', class_='session-item')
            for session_div in session_divs:
                session_data = {}
                
                # Session title
                title_elem = session_div.find('h3') or session_div.find('h4') or session_div.find('a', class_='session-title')
                if title_elem:
                    session_data['title'] = title_elem.get_text(strip=True)
                
                # Session time/date
                time_elem = session_div.find('div', class_='session-time') or session_div.find('span', class_='time')
                if time_elem:
                    session_data['time'] = time_elem.get_text(strip=True)
                
                # Session description
                desc_elem = session_div.find('div', class_='session-description') or session_div.find('p')
                if desc_elem:
                    session_data['description'] = desc_elem.get_text(strip=True)
                
                if session_data:
                    sessions.append(session_data)
            
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
            print(f"    Error fetching speaker details: {e}")
            return {
                'bio': "N/A",
                'topics': "N/A",
                'sessions': "N/A"
            }
    
    def extract_speaker_data(self, speaker_elem, event_date_place, save_debug=False):
        """Extract all data for a single speaker"""
        try:
            soup = BeautifulSoup(str(speaker_elem), 'html.parser')
            
            # Extract Name - look for speaker-name class inside h3
            name = "N/A"
            name_elem = soup.find('h3', class_='speaker-name')
            if name_elem:
                name = name_elem.get_text(strip=True)
            
            # If no name found, skip this element
            if name == "N/A" or len(name) < 3:
                return None
            
            # Extract Role/Designation - look for jobTitle class
            role = "N/A"
            role_elem = soup.find('div', class_='jobTitle')
            if role_elem:
                role = role_elem.get_text(strip=True)
            
            # Extract Company
            company = "N/A"
            company_elem = soup.find('div', class_='company')
            if company_elem:
                company = company_elem.get_text(strip=True)
                # Append company to role if both exist
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
            
            # Extract social media links from the footer area
            social = {
                'YouTube': '',
                'Twitter': '',
                'LinkedIn': '',
                'Facebook': '',
                'Instagram': ''
            }
            
            # Look for social links in the page footer or speaker card
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
            
            # Extract email (if available)
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
            import traceback
            traceback.print_exc()
            return None
    
    def scrape(self):
        """Main scraping function"""
        print(f"Starting {self.site_name} scraper...")
        
        try:
            self.setup_driver()
            print("Loading page...")
            self.driver.get(self.base_url)
            
            # Wait for page to load
            time.sleep(8)
            
            # Scroll down to load all speakers (lazy loading)
            print("Scrolling to load all content...")
            for _ in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            # Get page source
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Extract event date and place
            event_date_place = self.extract_event_info(soup)
            print(f"Event: {event_date_place}")
            
            # Find all speaker elements
            # Based on the HTML structure, speakers are in <a class="speaker-block member"> elements
            speaker_containers = soup.find_all('a', class_='speaker-block')
            
            print(f"Found {len(speaker_containers)} potential speaker elements")
            
            results = []
            processed_names = set()  # Track processed speakers to avoid duplicates
            first_speaker = True  # Flag for debug HTML saving
            
            for i, speaker_elem in enumerate(speaker_containers, 1):
                print(f"Processing element {i}/{len(speaker_containers)}...")
                
                speaker_data = self.extract_speaker_data(speaker_elem, event_date_place, first_speaker)
                first_speaker = False  # Only save debug HTML for first speaker
                
                if speaker_data and speaker_data['Name'] != "N/A":
                    # Check for duplicates
                    if speaker_data['Name'] not in processed_names:
                        results.append(speaker_data)
                        processed_names.add(speaker_data['Name'])
                        print(f"  ✓ {speaker_data['Name']}")
                    else:
                        print(f"  - Skipping duplicate: {speaker_data['Name']}")
                
                # Add delay to avoid detection
                time.sleep(0.5)
            
            # Save to CSV
            if results:
                self.save_to_csv(results)
                print(f"\n✓ Successfully scraped {len(results)} speakers")
            else:
                print("\n✗ No speakers found. Saving page HTML for debugging...")
                # Save HTML for debugging
                debug_file = os.path.join(self.data_dir, 'gartner_debug.html')
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(page_source)
                print(f"Saved page HTML to: {debug_file}")
                print("Please check the HTML structure to update selectors.")
                
        except Exception as e:
            print(f"Error during scraping: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.driver:
                self.driver.quit()
        return all_speakers_data
    
    def save_to_csv(self, data):
        """Save scraped data to CSV"""
        keys = ['Name', 'Date and Place', 'Role/Designation', 'Speaker Topics', 'Speaker Bio', 
                'Sessions', 'Email ID', 'YouTube', 'Twitter', 'LinkedIn', 'Facebook', 'Instagram', 'Source URL']
        
        with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            writer.writerows(data)
        
        print(f"Saved {len(data)} records to {self.output_file}")

def main():
    scraper = GartnerScraper()
    return scraper.scrape()

if __name__ == "__main__":
    main()
