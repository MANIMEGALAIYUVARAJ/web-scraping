import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from backend.driver_utils import get_driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def debug_us_site():
    url = "https://financialbrandforum.com/speakers/"
    driver = get_driver(headless=True)
    try:
        print(f"Navigating to {url}...")
        driver.get(url)
        time.sleep(10) # Heavy wait for JS
        
        # Save source
        with open("c:/Users/MANIMEGALAI/Desktop/AIOne_Scrapper-main/backend/us_debug.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        
        # Save screenshot
        driver.save_screenshot("c:/Users/MANIMEGALAI/Desktop/AIOne_Scrapper-main/backend/us_debug.png")
        print("Debug files saved.")
        
        # Try to find speakers
        try:
            speakers = driver.find_elements(By.CSS_SELECTOR, "h3, h4, .speaker-name, .name")
            print(f"Found {len(speakers)} potential speaker name elements.")
            for i, s in enumerate(speakers[:10]):
                print(f"{i}: {s.text.strip()}")
        except: pass

    finally:
        driver.quit()

if __name__ == "__main__":
    debug_us_site()
