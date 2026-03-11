import os
import csv
import time
import random
from DrissionPage import ChromiumPage, ChromiumOptions

class LeadingAuthoritiesScraper:
    def __init__(self):
        self.base_url = "https://www.leadingauthorities.com/uk/speaker-search?f%5B0%5D=topics%3A9"
        self.site_name = "Leading Authorities"
        # Path relative to Backend folder
        self.data_dir = os.path.join(os.path.dirname(__file__), 'ScrapedData', 'LeadingAuthorities')
        os.makedirs(self.data_dir, exist_ok=True)
        self.output_file = os.path.join(self.data_dir, 'leading_authorities_speakers.csv')
        self.page = None

    def setup_driver(self):
        """Initialize DrissionPage"""
        print("Setting up DrissionPage...")
        try:
            co = ChromiumOptions()
            # co.headless(True) # Better to run headed for Cloudflare
            co.set_argument('--no-sandbox')
            co.set_argument('--disable-gpu')
            co.set_argument('--disable-dev-shm-usage')
            
            # This will connect to an existing browser if available, or start a new one
            self.page = ChromiumPage(co)
            print("Browser started successfully.")
        except Exception as e:
            print(f"Error setting up driver: {e}")
            raise

    def get_search_url(self, query, page_idx):
        """Constructs the search URL for a given query and page index"""
        base = "https://www.leadingauthorities.com/uk/speaker-search"
        params = []
        if query:
            params.append(f"search={query}")
        else:
            # Default to Finance topic (original behavior)
            params.append("f%5B0%5D=topics%3A9")
            
        if page_idx > 0:
            params.append(f"page={page_idx}")
            
        return f"{base}?{'&'.join(params)}"

    def random_delay(self, min_sec=1, max_sec=3):
        time.sleep(random.uniform(min_sec, max_sec))

    def extract_profile_details(self, profile_url):
        """Extracts details from a speaker's profile page"""
        print(f"  Visiting profile: {profile_url}")
        try:
            # Create a new tab for the profile to avoid disrupting the main list
            tab = self.page.new_tab(profile_url)
            self.random_delay(0.5, 1.5)
            
            # Extract Bio
            bio = "N/A"
            bio_ele = tab.ele('css:.speaker-bio') or tab.ele('css:.field--name-field-biography')
            if bio_ele:
                bio = bio_ele.text
            
            # Extract Topics
            topics = []
            topics_div = tab.ele('css:.speaker-topics') or tab.ele('css:.field--name-field-speaker-topics')
            if topics_div:
                for topic in topics_div.eles('css:.field__item'):
                    topics.append(topic.text)
            topics_str = ", ".join(topics) if topics else "N/A"

            # Extract Fees
            fees = "N/A"
            fees_div = tab.ele('css:.field--name-field-fee-range')
            if fees_div:
                 fees = fees_div.text

            # Extract Type
            speaker_type = "N/A"
            type_div = tab.ele('css:.field--name-field-speaker-type')
            if type_div:
                speaker_type = type_div.text

            tab.close()
            return {
                'Bio': bio,
                'Topics': topics_str,
                'Fees': fees,
                'Type': speaker_type
            }

        except Exception as e:
            print(f"  Error extracting profile: {e}")
            try:
                tab.close() # Ensure tab is closed on error
            except:
                pass
            return {'Bio': "Error", 'Topics': "Error", 'Fees': "Error", 'Type': "Error"}

    def scrape(self, query=None, limit=10):
        try:
            self.setup_driver()
            start_url = self.get_search_url(query, 0)
            print(f"Navigating to {start_url}...")
            self.page.get(start_url)
            self.random_delay(3, 5)
            
            # Handle Cloudflare manually if needed
            if "Just a moment" in self.page.title:
                print("Cloudflare challenge detected. Waiting...")
                time.sleep(10) 

            # Handle cookie consent
            try:
                cookie_btn = self.page.ele('#onetrust-accept-btn-handler')
                if cookie_btn:
                    cookie_btn.click()
                    print("Accepted cookies.")
                    self.random_delay(1, 2)
            except:
                pass

            speakers_data = []
            page_idx = 0
            
            while len(speakers_data) < limit:
                print(f"Scraping page index {page_idx}...")
                
                current_page_url = self.get_search_url(query, page_idx)
                
                if self.page.url != current_page_url:
                    print(f"Navigating to: {current_page_url}")
                    self.page.get(current_page_url)
                    self.random_delay(1.5, 3)

                # Check if we are blocked
                if "Just a moment" in self.page.title:
                    print("Still on Cloudflare page. Waiting longer...")
                    time.sleep(10)
                
                # Wait for items to load (especially important for AJAX views)
                print(f"Waiting for speakers to load on page {page_idx}...")
                items_found = False
                for _ in range(5): # Up to 15 seconds wait
                    if self.page.ele('css:.speaker-grid--item'):
                        items_found = True
                        break
                    self.random_delay(2, 3)
                
                if not items_found:
                    print(f"No speaker items found on page index {page_idx}. Stopping.")
                    # Debug HTML for analysis
                    debug_file = os.path.join(self.data_dir, f'debug_page_{page_idx}.html')
                    with open(debug_file, 'w', encoding='utf-8') as f:
                        f.write(self.page.html)
                    print(f"  Saved debug HTML to {debug_file}")
                    break
                
                cards = self.page.eles('css:.speaker-grid--item')
                print(f"Found {len(cards)} speakers on page index {page_idx}")
                
                for card in cards:
                    if len(speakers_data) >= limit:
                        break
                        
                    try:
                        # Name and Profile URL
                        name_elem = card.ele('css:.speaker-grid--title a')
                        name = name_elem.text.strip()
                        profile_url = name_elem.attr('href')
                        
                        # Role
                        role = "N/A"
                        role_elem = card.ele('css:.speaker-grid--description')
                        if role_elem:
                            role = role_elem.text.strip()

                        # Check relevance if query is provided
                        if query:
                            # Re-verify keywords in card context for precision
                            searchable = f"{name} {role}".lower()
                            # Bio preview might also be relevant
                            bio_prev = card.ele('css:.speaker-grid--speaker-bio')
                            if bio_prev: searchable += f" {bio_prev.text.lower()}"
                            
                            if query.lower() not in searchable:
                                continue

                        # Fees
                        fees = "N/A"
                        fees_elem = card.ele('css:.speaker-grid--gross-list')
                        if fees_elem:
                            fees = fees_elem.text.strip().replace('\n', '; ')
                            
                        # Bio (short)
                        bio = "N/A"
                        bio_elem = card.ele('css:.speaker-grid--speaker-bio')
                        if bio_elem:
                            bio = bio_elem.text.strip()

                        # Topics and Types
                        topics = []
                        types = []
                        tags_block = card.ele('css:.sp-detail--tags-block')
                        if tags_block:
                            for link in tags_block.eles('tag:a'):
                                href = link.attr('href')
                                text = link.text.strip()
                                if "topics" in href:
                                    topics.append(text)
                                elif "types" in href:
                                    types.append(text)

                        # Detailed profile extraction
                        detailed_info = self.extract_profile_details(profile_url)

                        extracted_data = {
                            'Name': name,
                            'Role': role,
                            'Role/Designation': role,
                            'Bio': detailed_info['Bio'] if detailed_info['Bio'] != "N/A" else bio, 
                            'Description': detailed_info['Bio'] if detailed_info['Bio'] != "N/A" else bio,
                            'Fees': detailed_info['Fees'] if detailed_info['Fees'] != "N/A" else fees,
                            'Topics': detailed_info['Topics'] if detailed_info['Topics'] != "N/A" else ", ".join(topics),
                            'Type': detailed_info['Type'] if detailed_info['Type'] != "N/A" else ", ".join(types),
                            'LinkedIn': 'N/A', # Site typically doesn't show directly
                            'Source URL': profile_url
                        }
                        
                        speakers_data.append(extracted_data)
                        print(f"✓ Extracted [{len(speakers_data)}/{limit}]: {name}")

                    except Exception as e:
                        print(f"Error extracting card: {str(e)}")
                        continue
                        
                # Prepare for next page
                page_idx += 1
                
                # Save data incrementally after each page
                self.save_to_csv(speakers_data)
                
            self.save_to_csv(speakers_data) # Final save if loop breaks cleanly

        except Exception as e:
            print(f"Critical error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.page:
                self.page.quit()
        return speakers_data

    def save_to_csv(self, data):
        if not data: return
        keys = list(data[0].keys())
        with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            writer.writerows(data)
        print(f"Saved {len(data)} records to {self.output_file}")

def main(query=None, limit=10):
    scraper = LeadingAuthoritiesScraper()
    return scraper.scrape(query=query, limit=limit)

if __name__ == "__main__":
    main()
