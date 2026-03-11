import time
import os
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from driver_utils import get_driver

def scrape_linkedin_jobs(query, limit=10, save_csv=False, debug=False):
    results = []
    
    # Use existing Chrome profile (consistent with articles scraper)
    # Use absolute path relative to this script (backend/chrome-profile)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    profile_path = os.path.join(base_dir, "chrome-profile")
    if not os.path.exists(profile_path):
        os.makedirs(profile_path)

    print(f"Starting LinkedIn Jobs Scraper for '{query}'...")
    
    # Initialize Driver
    driver = get_driver(headless=(not debug), profile_path=profile_path)
    wait = WebDriverWait(driver, 20)

    try:
        # 1. Go to LinkedIn Jobs Search
        search_url = f"https://www.linkedin.com/jobs/search/?keywords={query}"
        driver.get(search_url)
        time.sleep(5) # Wait for load

        # Login Check
        if "session_redirect" in driver.current_url or "login" in driver.current_url:
             print("WARNING: User is likely NOT logged in.")
             if debug:
                 input("Please log in manually, then press Enter...")
        
        # Scroll to load jobs
        print("Scrolling to load jobs...")
        last_height = driver.execute_script("return document.body.scrollHeight")
        for _ in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # 2. Find Job Cards
        # Try multiple selectors for job cards
        # Logged in: .job-card-container
        # Guest: .jobs-search__results-list > li
        job_cards = driver.find_elements(By.CSS_SELECTOR, ".job-card-container")
        is_guest = False
        if not job_cards:
            job_cards = driver.find_elements(By.CSS_SELECTOR, ".jobs-search__results-list > li")
            if job_cards:
                is_guest = True
                print("Using Guest Mode selectors.")
        
        print(f"Found {len(job_cards)} potential job cards. Guest Mode: {is_guest}")

        for card in job_cards:
            if len(results) >= limit:
                break
            
            try:
                # Scroll card into view
                driver.execute_script("arguments[0].scrollIntoView();", card)
                
                # Extract Data
                title = "Unknown"
                company = "Unknown" 
                location = "Unknown"
                date = "Recent"
                job_url = ""

                if not is_guest:
                    # LOGGED IN SELECTORS
                    try:
                        title_elem = card.find_element(By.CSS_SELECTOR, ".job-card-list__title")
                        title = title_elem.text.strip()
                        job_url = title_elem.get_attribute("href").split('?')[0]
                    except: pass

                    try:
                        company = card.find_element(By.CSS_SELECTOR, ".job-card-container__company-name").text.strip()
                    except: pass

                    try:
                        location = card.find_element(By.CSS_SELECTOR, ".job-card-container__metadata-item").text.strip()
                    except: pass
                        
                    try:
                        date = card.find_element(By.CSS_SELECTOR, "time").get_attribute("datetime")
                    except: pass
                
                else:
                    # GUEST MODE SELECTORS
                    try:
                        title_elem = card.find_element(By.CSS_SELECTOR, ".base-search-card__title")
                        title = title_elem.text.strip()
                    except: pass
                    
                    try:
                        # Guest URL is often on the anchor wrapping the card or title
                        link_elem = card.find_element(By.CSS_SELECTOR, ".base-card__full-link")
                        job_url = link_elem.get_attribute("href").split('?')[0]
                    except: pass

                    try:
                        company = card.find_element(By.CSS_SELECTOR, ".base-search-card__subtitle").text.strip()
                    except: pass

                    try:
                        location = card.find_element(By.CSS_SELECTOR, ".job-search-card__location").text.strip()
                    except: pass
                    
                    try:
                        date = card.find_element(By.CSS_SELECTOR, "time").get_attribute("datetime")
                    except: pass

                if title != "Unknown":
                    results.append({
                        "platform": "LinkedIn",
                        "query": query,
                        "job_title": title,
                        "company_name": company,
                        "job_location": location,
                        "post_time": date,
                        "job_url": job_url,
                        "job_description": "Click link for details", 
                        "salary": "N/A"
                    })
                
            except Exception as e:
                print(f"Error parsing job card: {e}")
                continue

    except Exception as e:
        print(f"Critical Error during scraping: {e}")
    
    finally:
        driver.quit()

    # Save Results
    if save_csv and results:
        df = pd.DataFrame(results)
        filename = "linkedin_jobs.csv"
        df.to_csv(filename, index=False, encoding="utf-8-sig")
        print(f"Saved {len(results)} jobs to {filename}")
    
    return results

if __name__ == "__main__":
    # Test run
    scrape_linkedin_jobs("python developer", limit=5, debug=True)
