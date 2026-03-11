# backend/restaurant_scraper.py
import time
import csv
import random
import os
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from driver_utils import get_driver

# Output config
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def start_driver(headless=True):
    # Use centralized driver configuration
    # TripAdvisor detects headless easily, defaulting to False for now or using stealth
    # The new driver_utils should handle stealth args
    return get_driver(headless=headless)

def wait():
    time.sleep(random.uniform(2, 4))

def safe_text(driver, xpath):
    try:
        return driver.find_element(By.XPATH, xpath).text.strip()
    except:
        return ""

def safe_href(driver, xpath):
    try:
        return driver.find_element(By.XPATH, xpath).get_attribute("href") or ""
    except:
        return ""


def find_tripadvisor_url(driver, query):
    print(f"🔍 Searching TripAdvisor for: {query}")
    driver.get("https://www.tripadvisor.com/Restaurants")
    wait()
    
    # CHECK FOR ACCESS RESTRICTION
    if "restricted" in driver.title.lower() or "denied" in driver.title.lower():
        print("⚠️  ACCESS RESTRICTED DETECTED!")
        print("Please solve the CAPTCHA or slide the verification puzzle in the browser window manually.")
        input("Press Enter here AFTER you have solved it and see the normal homepage...")
        wait()

    # HARRIS CHECK: CAPTCHA / Security Challenge
    # Instead of looking for specific text, we loop until we find the SEARCH BOX.
    # If we can't find it, we assume the user is solving a captcha.
    
    search_box = None
    selectors = [
        "form input[name='q']", 
        "input[type='search']", 
        "div[data-test-target='search-input'] input",
        "input[placeholder*='Search']"
    ]
    
    print("Waiting for Search Box or User to solve Captcha...")
    for i in range(120): # Try for 2 minutes
        # Re-check for restriction during wait
        if "restricted" in driver.title.lower():
             print("⚠️  Still restricted. Please solve CAPTCHA manually.")
        
        # Try to find search box
        for css in selectors:
            try:
                inputs = driver.find_elements(By.CSS_SELECTOR, css)
                if inputs and inputs[0].is_displayed():
                    search_box = inputs[0]
                    break
            except: pass
        
        if search_box:
            print("Search box found!")
            break
            
        if i % 10 == 0:
            print(f"Waiting for search box... (Attempt {i}/120). Please solve any CAPTCHA on screen.")
        time.sleep(1)

    try:
        # Search box already found above
        if search_box:
            # Re-fetch to avoid stale element
             for css in selectors:
                try:
                    inputs = driver.find_elements(By.CSS_SELECTOR, css)
                    if inputs and inputs[0].is_displayed():
                        search_box = inputs[0]
                        break
                except: pass
            
        if search_box:
            search_box.click()
            search_box.clear()
            # Human-like typing
            for char in query:
                search_box.send_keys(char)
                time.sleep(random.uniform(0.05, 0.2))
            
            time.sleep(1.5)
            search_box.send_keys(Keys.ENTER)
            print("Entered query, waiting for results...")
            time.sleep(5)
            
            # If we land on a search results page, find the first "Geo" or "Location" link
            if "Search" in driver.title or "search" in driver.current_url.lower():
                print("On Search Results page, selecting first result...")
                try:
                    # Look for result titles
                    results = driver.find_elements(By.CSS_SELECTOR, ".result-title, .result-content a, div[data-widget='result-title']")
                    if results:
                        driver.execute_script("arguments[0].click();", results[0])
                        time.sleep(5)
                except Exception as e:
                    print(f"Error selecting result: {e}")
            
            # Check for restriction again after navigation
            if "restricted" in driver.title.lower():
                 print("⚠️  Access Restricted after search. Please solve manually.")
                 input("Press Enter after solving...")

            # If we are now on a Restaurants page
            if "Restaurants" in driver.current_url:
                print(f"Found match: {driver.current_url}")
                return driver.current_url
                
            print(f"Current URL after search: {driver.current_url}")
            return driver.current_url
            
    except Exception as e:
        print(f"Search failed: {e}")
        
    return None

def scrape_city(driver, city_name, city_url, limit, csv_writer):
    print(f"\n🟢 Scraping: {city_name} ({city_url})")
    if driver.current_url != city_url:
        driver.get(city_url)
        wait()
        
    scraped_links = set()
    total = 0
    page = 1
    
    # Ensure limit is int
    limit = int(limit)

    while total < limit:
        print(f"📄 Page {page} (Collected: {total})")
        
        # Collect restaurant cards
        # TripAdvisor selectors for restaurant list
        restaurant_cards = driver.find_elements(By.XPATH, '//div[contains(@class,"geo_name")]/a | //a[contains(@href,"/Restaurant_Review-")]')
        
        # Deduplicate on page
        page_urls = []
        for r in restaurant_cards:
            u = r.get_attribute("href")
            if u and "Restaurant_Review" in u and u not in scraped_links:
                page_urls.append(u)
                scraped_links.add(u)
        
        # Process links
        for url in page_urls:
            if total >= limit:
                break
                
            driver.execute_script("window.open(arguments[0]);", url)
            driver.switch_to.window(driver.window_handles[-1])
            wait()
            
            try:
                name = safe_text(driver, "//h1")
                if name:
                    phone = safe_text(driver, "//a[contains(@href,'tel:')]")
                    website = safe_href(driver, "//a[contains(text(),'Website')]")
                    email = safe_href(driver, "//a[contains(text(),'Email')]").replace("mailto:", "")
                    rating = safe_text(driver, "//span[contains(@class,'ui_bubble_rating')]") # older selector
                    if not rating: rating = safe_text(driver, "//svg[contains(@title, 'of 5 bubbles')]/title")
                    
                    reviews = safe_text(driver, "//a[contains(@href,'#REVIEWS')]")
                    # Address - looks for the map pin icon usually or class
                    address = safe_text(driver, "//span[contains(@class,'biGQs')] | //a[@href='#MAPVIEW']") 

                    # Map to frontend keys (restaurant_name, city, etc defined in config)
                    csv_writer.writerow([
                        city_name, name, phone, website, email, reviews, rating, address, url
                    ])
                    total += 1
                    print(f"✅ {total}. {name}")
            except Exception as e:
                print(f"Error scraping detail: {e}")
                
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            # wait() # speed up

        if total >= limit:
            break
            
        # Next Page
        try:
            next_btns = driver.find_elements(By.CSS_SELECTOR, "a.nav.next, a[data-smoke-attr='pagination-next-arrow']")
            if next_btns:
                driver.execute_script("arguments[0].click();", next_btns[0])
                page += 1
                wait()
            else:
                print("🚫 No more pages")
                break
        except:
             print("🚫 Pagination failed")
             break

def scrape_restaurant(query=None, limit=30):
    limit = int(limit)
    filename = f"tripadvisor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    output_file = os.path.join(OUTPUT_DIR, filename)

    # Use headless=False because TripAdvisor is tough on bots
    driver = start_driver(headless=False)

    try:
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            # Keys matching frontend: city, restaurant_name, phone, website, email, reviews, rating, address, tripadvisor_url
            writer.writerow([
                "city", "restaurant_name", "phone", "website", "email",
                "reviews", "rating", "address", "tripadvisor_url"
            ])
            
            if query:
                # Dynamic Search
                target_url = find_tripadvisor_url(driver, query)
                if target_url:
                    scrape_city(driver, query, target_url, limit, writer)
                else:
                    print("Could not find location logic.")
            else:
                # Default behavior if no query
                defaults = [("New York", "https://www.tripadvisor.com/Restaurants-g60763-New_York_City_New_York.html")]
                for city, url in defaults:
                    scrape_city(driver, city, url, limit, writer)

    finally:
        driver.quit()
        
    print(f"\n🎉 Restaurant scraping completed! Saved at: {output_file}")
    return output_file

if __name__ == "__main__":
    scrape_restaurant("Paris", limit=5)
