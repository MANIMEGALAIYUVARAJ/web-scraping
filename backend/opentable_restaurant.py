import os
import time
import json
import csv
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from driver_utils import get_driver

# ---------------- DRIVER SETUP ----------------
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def start_driver(headless=True):
    return get_driver(headless=headless)

def save_csv(data):
    if not data:
        return None
    filename = f"opentable_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    return path

# ---------------- URL BUILDER ----------------
def build_opentable_url(country, city):
    base_url = "https://www.opentable.com/"
    return base_url

# ---------------- MAIN SCRAPER ----------------
def scrape_opentable(country, city, limit=10, headless=True):
    query = f"{city}"
    # If a state or country is provided, maybe append it, but usually City is enough
    if len(city) < 4 and country:
        query += f" {country}"

    url = build_opentable_url(country, city)
    print(f"🌍 OpenTable Base URL: {url}")
    
    driver = start_driver(headless=headless)
    results = []
    
    try:
        # 1. Load Homepage
        driver.get(url)
        time.sleep(3)

        # 2. Perform Search
        print(f"Performing search for '{query}'...")
        try:
             # Try multiple potential selectors for the search bar
             search_inputs = driver.find_elements(By.CSS_SELECTOR, "input[data-test='search-autocomplete-input'], input[role='combobox'], input[type='text']")
             if not search_inputs:
                 print("Could not find search bar.")
                 return []
             
             search_box = search_inputs[0]
             search_box.clear()
             search_box.send_keys(query)
             time.sleep(1)
             search_box.send_keys(Keys.ENTER)
             
             # Wait for results to load
             time.sleep(5)
             WebDriverWait(driver, 15).until(lambda d: d.execute_script("return document.readyState") == "complete")
             
        except Exception as e:
            print(f"Search interaction failed: {e}")
            return []

        # 3. Parse JSON Data from Script Tag
        print("Extracting data from JSON...")
        try:
            # The data is usually in a script tag with id="primary-window-vars" or "__NEXT_DATA__" or similar.
            script_content = None
            try:
                elem = driver.find_element(By.ID, "primary-window-vars")
                script_content = elem.get_attribute("innerHTML")
            except:
                # Fallback: search for script containing specific key
                scripts = driver.find_elements(By.TAG_NAME, "script")
                for s in scripts:
                    try:
                        txt = s.get_attribute("innerHTML")
                        if txt and "windowVariables" in txt and "multiSearch" in txt:
                            script_content = txt
                            break
                    except: continue
            
            if script_content:
                data = json.loads(script_content)
                
                # Structure: windowVariables -> __INITIAL_STATE__ -> multiSearch -> restaurants
                root = data.get("windowVariables", {})
                state = root.get("__INITIAL_STATE__", {})
                multi_search = state.get("multiSearch", {})
                restaurant_list = multi_search.get("restaurants", [])
                
                print(f"Found {len(restaurant_list)} restaurants in JSON data.")
                
                for r in restaurant_list:
                    if len(results) >= limit:
                        break
                        
                    # Extract fields
                    try:
                        name = r.get("name", "-")
                        if name == "-": continue
                        
                        # Rating
                        reviews = r.get("statistics", {}).get("reviews", {})
                        rating = reviews.get("ratings", {}).get("overall", {}).get("rating", "-")
                        review_count = reviews.get("allTimeTextReviewCount", "-")
                        
                        # Price
                        price_band = r.get("priceBand", {}).get("name", "-")
                        
                        # Cuisine
                        cuisine = r.get("primaryCuisine", {}).get("name", "-")
                        
                        # Contact / Location
                        address_obj = r.get("address", {})
                        # format address
                        addr_parts = [address_obj.get(k) for k in ["line1", "city", "state"] if address_obj.get(k)]
                        location = ", ".join(addr_parts)
                        
                        phone = r.get("contactInformation", {}).get("formattedPhoneNumber", "-")
                        
                        # Description
                        desc = r.get("description", "-")
                        if desc and len(desc) > 300:
                            desc = desc[:300] + "..."
                            
                        # URL
                        profile_link = r.get("urls", {}).get("profileLink", {}).get("link", "")
                        
                        results.append({
                            "restaurant_name": name,
                            "rating": str(rating),
                            "reviews_count": str(review_count),
                            "price": price_band,
                            "cuisine": cuisine,
                            "location": location,
                            "phone": phone,
                            "description": desc,
                            "source_url": profile_link,
                            "country": country,
                            "city": city
                        })
                    except Exception as e:
                        print(f"Error parsing restaurant item: {e}")
                        continue
                        
            else:
                print("Could not find data script tag in page source.")
                
        except Exception as e:
            print(f"JSON Parsing failed: {e}")

        # 4. Fallback (if JSON failed) - Implement a basic check or just return what we have
        if not results:
             print("No results found via JSON. The structure might have changed.")

        save_csv(results)
        return results

    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_opentable("us", "new york", limit=5, headless=False)
