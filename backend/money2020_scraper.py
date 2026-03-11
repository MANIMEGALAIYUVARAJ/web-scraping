import time
import csv
import random
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import sys
import os
sys.path.append(os.path.dirname(__file__))
from driver_utils import get_driver

class Money2020Scraper:
    def __init__(self, region='Europe', site_name='Money2020 Europe', base_url=None):
        self.region = region
        self.site_name = site_name
        self.base_url = base_url or 'https://europe.money2020.com/speakers'
        self.driver = None

    def setup_driver(self, headless=True):
        print(f"Setting up driver for {self.site_name}...")
        self.driver = get_driver(headless=headless)
        self.driver.set_page_load_timeout(30)

    def wait_random(self, min_s=1, max_s=3):
        time.sleep(random.uniform(min_s, max_s))

    def scrape(self, query=None, limit=10, debug=False):
        if not self.driver:
            self.setup_driver()

        results = []
        try:
            print(f"Navigating to {self.base_url}...")
            self.driver.get(self.base_url)
            
            wait = WebDriverWait(self.driver, 20)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            self.wait_random(5, 8) # Wait for initial JS load

            # Handle search if query is provided
            if query:
                print(f"Performing search for: {query}")
                try:
                    # Search input can be #search or data-testid='search'
                    search_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[id='search'], input[data-testid='search'], input[type='search'], #search")))
                    search_input.clear()
                    search_input.send_keys(query)
                    self.wait_random(1, 2)
                    search_input.send_keys(Keys.ENTER)
                    print("Search query submitted.")
                    self.wait_random(5, 8)
                except Exception as e:
                    print(f"Search failed: {e}. Proceeding with general scrape...")

            if debug:
                debug_dir = os.path.join(os.path.dirname(__file__), 'ScrapedData', self.region)
                os.makedirs(debug_dir, exist_ok=True)
                self.driver.save_screenshot(os.path.join(debug_dir, "debug.png"))
                with open(os.path.join(debug_dir, "debug.html"), "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
                print(f"Saved debug files to {debug_dir}")

            # Wait for results to be visible
            print("Waiting for speaker cards to load...")
            try:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='card']")))
            except:
                print("Results container not found via testid, trying general wait...")
                self.wait_random(5, 8)

            # Collect speaker links/info from the list
            potential_cards = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='card'], .eo8h9sq0")
            print(f"Found {len(potential_cards)} cards via CSS.")
            
            speaker_cards = []
            if potential_cards:
                for card in potential_cards:
                    try:
                        if card.tag_name == "a":
                            speaker_cards.append(card)
                        else:
                            link = card.find_element(By.XPATH, ".//ancestor-or-self::a")
                            if link not in speaker_cards:
                                speaker_cards.append(link)
                    except:
                        try:
                            parent_a = card.find_element(By.XPATH, "./parent::a")
                            if parent_a not in speaker_cards:
                                speaker_cards.append(parent_a)
                        except: continue
            
            if not speaker_cards:
                print("No cards found via specific selectors, falling back to general link search...")
                all_links = self.driver.find_elements(By.TAG_NAME, "a")
                for link in all_links:
                    try:
                        href = link.get_attribute("href")
                        if href and ("/speakers/" in href or "/agenda/speakers/" in href):
                            if not any(href == card.get_attribute("href") for card in speaker_cards):
                                speaker_cards.append(link)
                    except: continue

            print(f"Final count: {len(speaker_cards)} potential speaker cards identified.")

            processed_urls = set()
            
            temp_results = []
            for card in speaker_cards:
                if len(temp_results) >= 50:
                    break
                
                try:
                    href = card.get_attribute("href")
                    if not href or href in processed_urls:
                        continue
                    processed_urls.add(href)

                    name = "Unknown"
                    try:
                        name_elem = card.find_element(By.CSS_SELECTOR, "[data-testid='content-profile-name'], [data-testid='media-profile-name'], h3, h4")
                        name = name_elem.text.strip()
                    except: pass
                    
                    if name == "Unknown" or len(name) < 2:
                        name = card.text.strip().split('\n')[0]

                    temp_results.append({
                        'Name': name,
                        'Email ID': 'Not Public',
                        'Role': 'Loading...',
                        'Bio': 'N/A',
                        'Speaking Sessions': 'N/A',
                        'LinkedIn': 'N/A',
                        'Source URL': href
                    })
                except: continue

            print(f"Extracted basic info for {len(temp_results)} speakers. Fetching details...")
            
            final_results = []
            for item in temp_results:
                if len(final_results) >= limit:
                    break
                    
                print(f"Fetching details for {item['Name']}...")
                try:
                    self.driver.get(item['Source URL'])
                    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                    self.wait_random(3, 5)
                    
                    # Update name if more precise one found
                    try:
                        item['Name'] = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='content-profile-name']").text.strip()
                    except: pass
                    
                    # Role/Designation
                    try:
                        role = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='job-title']").text.strip()
                        company = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='company-name']").text.strip()
                        item['Role'] = f"{role} at {company}"
                        item['Role/Designation'] = item['Role']
                    except:
                        try:
                            item['Role'] = self.driver.find_element(By.CSS_SELECTOR, ".job-title").text.strip()
                            item['Role/Designation'] = item['Role']
                        except:
                            item['Role'] = "N/A"
                            item['Role/Designation'] = "N/A"

                    # Bio
                    bio_found = False
                    try:
                        bio_section = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='biography'], .speaker-bio, .bio")
                        item['Bio'] = bio_section.text.strip()
                        if len(item['Bio']) > 20: bio_found = True
                    except: pass
                    
                    if not bio_found:
                        try:
                            headings = self.driver.find_elements(By.XPATH, "//*[self::h1 or self::h2 or self::h3][contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'biography')]")
                            if headings:
                                parent = headings[0].find_element(By.XPATH, "..")
                                bio_text = parent.text.split(headings[0].text)[-1].strip()
                                if len(bio_text) > 30:
                                    item['Bio'] = bio_text
                                    bio_found = True
                        except: pass

                    if not bio_found:
                        try:
                            ps = [p.text.strip() for p in self.driver.find_elements(By.TAG_NAME, "p") if len(p.text.strip()) > 50]
                            ps = [p for p in ps if not any(x in p.lower() for x in ["copyright", "privacy", "cookies", "terms"])]
                            if ps: item['Bio'] = "\n\n".join(ps[:3])
                        except: pass

                    # Speaking Sessions
                    try:
                        sessions = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='session-title'], .session-title, .agenda-item-title")
                        if sessions:
                            item['Speaking Sessions'] = " | ".join([s.text.strip() for s in sessions if s.text.strip()])
                    except: pass

                    # LinkedIn
                    try:
                        item['LinkedIn'] = self.driver.find_element(By.XPATH, "//a[contains(@href, 'linkedin.com/in/')]").get_attribute("href")
                    except:
                        try:
                            links = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'linkedin.com')]")
                            for l in links:
                                href = l.get_attribute("href")
                                if "company/money2020" not in href.lower() and "share" not in href.lower():
                                    item['LinkedIn'] = href
                                    break
                        except: pass

                    # Finalize tags
                    item['Description'] = item['Bio']
                    if item.get('Speaking Sessions') and item['Speaking Sessions'] != 'N/A':
                        item['Description'] += f"\n\nSpeaking Sessions:\n{item['Speaking Sessions']}"
                    
                    item['Description'] += f"\n\nPost URL: {item['Source URL']}"

                    # Post-scrape filtering
                    if query:
                        searchable = f"{item['Name']} {item['Role']} {item['Bio']} {item['Speaking Sessions']}".lower()
                        if query.lower() not in searchable:
                            print(f"Skipping {item['Name']} - query '{query}' not found.")
                            continue

                    final_results.append(item)
                    print(f"✓ Added: {item['Name']}")
                    
                except Exception as e:
                    print(f"Error for {item['Name']}: {e}")
                    if not query or query.lower() in item['Name'].lower():
                        final_results.append(item)

            return final_results

        except Exception as e:
            print(f"Scrape error: {e}")
            import traceback
            traceback.print_exc()
            return results[:limit]
        finally:
            if self.driver:
                self.driver.quit()

def main(query=None, limit=10, debug=False):
    scraper = Money2020Scraper()
    return scraper.scrape(query=query, limit=limit, debug=debug)

if __name__ == "__main__":
    data = main(query="CEO", limit=5, debug=True)
    print(f"Scraped {len(data)} results.")
    for d in data:
        print(f"- {d['Name']} ({d.get('Role/Designation', 'N/A')})")
