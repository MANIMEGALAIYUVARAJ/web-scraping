import time
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from driver_utils import get_driver

BASE_URL = "https://www.eauctionsindia.com"

def scrape_eauctionsindia(place: str, limit: int = 10):
    driver = get_driver(headless=False)
    wait = WebDriverWait(driver, 15)
    scraped = 0
    
    try:
        # Go to Homepage
        driver.get(BASE_URL)
        time.sleep(3)
        
        # Try to find search bar and search
        # If specific city URL logic is preferred, we can fallback, but search is better for "Keywords"
        try:
            search_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='keyword'], input[id='keyword'], input[placeholder*='Auction Id']")))
            search_input.clear()
            search_input.send_keys(place)
            search_input.send_keys(Keys.RETURN)
            time.sleep(5)
        except Exception as e:
            print(f"Search bar not found or failed: {e}")
            # Fallback to loose city url if search fails, though likely won't work for keywords
            pass

        # Scroll for results
        for _ in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)

        # Collect links
        links = []
        try:
            # Look for property links
            elements = driver.find_elements(By.CSS_SELECTOR, "a[href^='https://www.eauctionsindia.com/properties/']")
            if not elements:
                 elements = driver.find_elements(By.XPATH, "//a[contains(@href, '/properties/')]")
            
            for a in elements:
                href = a.get_attribute("href")
                if href and href not in links:
                    links.append(href)
        except:
             pass
        
        links = list(dict.fromkeys(links))[:limit]
        print(f"Found {len(links)} auctions for '{place}'")

        # Scrape Details
        for url in links:
            if scraped >= limit:
                break
            try:
                driver.get(url)
                time.sleep(1.5)
                
                def get_by_label(label):
                    try:
                        # Try exact match first, then efficient contains
                        el = driver.find_element(
                            By.XPATH,
                            f"//strong[contains(text(),'{label}')]/parent::div | //strong[contains(normalize-space(),'{label}')]/parent::div"
                        )
                        return el.text.replace(label, "").replace(":", "").strip()
                    except:
                        return ""

                row = {
                    "url": url,
                    "bank": get_by_label("Bank Name"),
                    "property_type": get_by_label("Property Type"),
                    "reserve_price": get_by_label("Reserve Price"),
                    "emd": get_by_label("EMD"),
                    "auction_date": get_by_label("Auction Date"),
                    "branch": get_by_label("Branch Name"),
                    "contact": get_by_label("Contact Details"),
                    "city": get_by_label("City/Town"),
                    "area": get_by_label("Area/Town"),
                }
                
                try:
                    row["description"] = driver.find_element(
                        By.CSS_SELECTOR, ".card-body p, .property-description"
                    ).text.strip()
                except:
                    row["description"] = ""
                
                scraped += 1
                yield row
                
            except Exception as e:
                print(f"Error scraping {url}: {e}")
                continue

    finally:
        driver.quit()
