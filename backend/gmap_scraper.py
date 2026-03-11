# backend/gmap_scraper.py
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from driver_utils import get_driver

def scroll_until_enough_results(driver, min_results=20, max_scrolls=30):
    last_count = 0
    # Try finding the feed list first
    try:
        wait = WebDriverWait(driver, 10)
        # Verify if the feed element exists
        feed = wait.until(EC.presence_of_element_located((By.XPATH, '//div[contains(@aria-label, "Results for")]')))
    except:
        pass

    for _ in range(max_scrolls):
        try:
            # Scroll the feed container
            driver.execute_script(
                "arguments[0].scrollBy(0,1000);", 
                driver.find_element(By.XPATH, '//div[contains(@aria-label, "Results for")]')
            )
            time.sleep(2)
            cards = driver.find_elements(By.CSS_SELECTOR, "a.hfpxzc")
            if len(cards) >= min_results:
                break
            if len(cards) == last_count:
                # small wait to see if more load
                time.sleep(1)
            last_count = len(cards)
        except:
            break

import re

def clean_text(text):
    """Clean unwanted characters and icon glyphs from text."""
    if not text:
        return "N/A"
    # Remove common Google Maps glyph icons (Private Use Area characters)
    # These often show up as îƒˆ or similar when copied/scraped
    text = re.sub(r'[\ue000-\uf8ff]', '', text)
    # Remove other non-essential whitespace/newlines
    text = re.sub(r'\s+', ' ', text).strip()
    return text if text else "N/A"

def extract_email_from_website(driver, url):
    """Visit website and try to extract email using regex."""
    if not url or url == "N/A" or "google.com" in url:
        return "N/A"
    
    try:
        print(f"  Attempting email extraction from: {url}")
        driver.get(url)
        time.sleep(3) # Wait for load
        
        page_source = driver.page_source
        # Robust email regex
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, page_source)
        
        if emails:
            # Filter out common junk or image extensions if caught by regex
            valid_emails = []
            for email in emails:
                if not any(email.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp']):
                    valid_emails.append(email)
            
            if valid_emails:
                # Deduplicate and return first
                return list(dict.fromkeys(valid_emails))[0]
                
    except Exception as e:
        print(f"  Warning: Could not extract email from {url}: {e}")
        
    return "N/A"

def parse_place_page(driver, url):
    data = {
        "name": "N/A",
        "rating": "N/A",
        "address": "N/A",
        "phone": "N/A",
        "website": "N/A",
        "email": "N/A",
        "url": url,
    }

    try:
        driver.get(url)
        # Increased wait for stable load
        wait = WebDriverWait(driver, 15)
        
        # Wait for the main container or heading
        try:
            name_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.DUwDfb, h1")))
            data["name"] = clean_text(name_elem.text)
        except:
            pass

        # Robust Address extraction
        try:
            # Try data-item-id first
            address_elem = driver.find_element(By.CSS_SELECTOR, '[data-item-id="address"]')
            data["address"] = clean_text(address_elem.get_attribute("aria-label").replace("Address: ", ""))
            if data["address"] == "N/A":
                data["address"] = clean_text(address_elem.text)
        except:
            # Fallback for address
            try:
                addr_btn = driver.find_element(By.XPATH, '//button[contains(@aria-label, "Address:")]')
                data["address"] = clean_text(addr_btn.get_attribute("aria-label").replace("Address: ", ""))
            except:
                pass

        # Robust Phone extraction
        try:
            phone_elem = driver.find_element(By.CSS_SELECTOR, '[data-item-id^="phone:tel:"]')
            data["phone"] = clean_text(phone_elem.get_attribute("aria-label").replace("Phone: ", ""))
            if data["phone"] == "N/A":
                 data["phone"] = clean_text(phone_elem.text)
        except:
            pass

        # Website extraction
        try:
            website_elem = driver.find_element(By.CSS_SELECTOR, '[data-item-id="authority"]')
            data["website"] = website_elem.get_attribute("href") or clean_text(website_elem.text)
            
            # If we found a website, try to extract email
            if data["website"] != "N/A":
                data["email"] = extract_email_from_website(driver, data["website"])
        except:
            pass

        # Robust Rating extraction
        try:
            # 1. Search for any element with "stars" in aria-label
            stars_elems = driver.find_elements(By.XPATH, '//*[contains(@aria-label, "stars")]')
            for el in stars_elems:
                label = el.get_attribute("aria-label")
                match = re.search(r"(\d+(\.\d+)?)", label)
                if match:
                    data["rating"] = match.group(1)
                    break
            
            # 2. Fallback to specific classes if still N/A
            if data["rating"] == "N/A":
                selectors = ['.ceNzR', '.fontBodyMedium span[aria-label]', 'div[role="img"]']
                for s in selectors:
                    try:
                        elems = driver.find_elements(By.CSS_SELECTOR, s)
                        for el in elems:
                            txt = el.get_attribute("aria-label") or el.text
                            match = re.search(r"(\d+(\.\d+)?)", txt)
                            if match:
                                data["rating"] = match.group(1)
                                return data # Found it
                    except:
                        continue
        except:
            pass

    except Exception as e:
        print(f"Error parsing place page {url}: {e}")

    return data

def scrape_gmap(query="restaurants in Chennai", max_places=20, headless=True, region=None):
    # Use centralized driver
    driver = get_driver(headless=headless)
    
    try:
        # Avoid local redirects by using .com and gl parameter if region is provided
        base_search_url = "https://www.google.com/maps/search/"
        url_query = query.replace(' ', '+')
        search_url = f"{base_search_url}{url_query}"
        
        # Add region/language bias
        params = []
        if region:
            params.append(f"gl={region}")
        params.append("hl=en") # Force English for consistent parsing
        
        if params:
            search_url += "?" + "&".join(params)

        print(f"Searching: {search_url}")
        driver.get(search_url)
        time.sleep(5)

        scroll_until_enough_results(driver, min_results=max_places)

        place_elements = driver.find_elements(By.CSS_SELECTOR, "a.hfpxzc")
        urls = []
        for el in place_elements:
            href = el.get_attribute("href")
            if href:
                urls.append(href)

        urls = list(dict.fromkeys(urls))
        print(f"Found {len(urls)} places. Scraping details...")

        results = []
        for url in urls[:max_places]:
            print(f"Scraping: {url}")
            results.append(parse_place_page(driver, url))
            time.sleep(1)

        return results
    finally:
        driver.quit()

def scrape_google_maps(query, limit=20):
    return scrape_gmap(query=query, max_places=limit)
