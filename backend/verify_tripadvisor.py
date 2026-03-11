import sys
import os
import time

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from restaurant_scraper import scrape_restaurant, start_driver, find_tripadvisor_url

def verify_access():
    print("=== TripAdvisor Verification ===")
    print("This script will attempt to search for restaurants in 'Paris'.")
    print("If an 'Access Restricted' page appears, the script should pause and ask you to solve it.")
    print("---------------------------------------------------------")
    
    driver = start_driver(headless=False)
    
    try:
        url = find_tripadvisor_url(driver, "Paris")
        if url:
            print(f"\n✅ SUCCESSFULLY found URL: {url}")
            print("Access seems to be working!")
        else:
            print("\n❌ Failed to find URL. Access might still be blocked or selectors changed.")
            
    except Exception as e:
        print(f"\nERROR: {e}")
    finally:
        print("\nClosing driver in 5 seconds...")
        time.sleep(5)
        driver.quit()

if __name__ == "__main__":
    verify_access()
