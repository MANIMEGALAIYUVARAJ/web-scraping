from driver_utils import get_driver
import time

def verify_url():
    driver = get_driver(headless=False)
    try:
        url = "https://www.opentable.com/r/gran-morsi-new-york"
        print(f"Navigating to {url}...")
        driver.get(url)
        time.sleep(5)
        
        if "404" in driver.title or "not find" in driver.page_source:
             print("URL failed (404).")
        else:
             print("URL loaded successfully!")
             print(f"Title: {driver.title}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    verify_url()
