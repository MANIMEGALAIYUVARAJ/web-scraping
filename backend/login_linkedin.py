import time
import os
from driver_utils import get_driver

def login_linkedin():
    print("Opening LinkedIn for login...")
    print("Please log in to your account in the browser window that appears.")
    
    # Use absolute path relative to this script (backend/chrome-profile)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    profile_path = os.path.join(base_dir, "chrome-profile")
    if not os.path.exists(profile_path):
        os.makedirs(profile_path)
        
    # Initialize driver in HEADFUL mode (headless=False)
    driver = get_driver(headless=False, profile_path=profile_path)
    
    try:
        driver.get("https://www.linkedin.com/login")
        print("\nBrowser is open. Please log in manually.")
        print("Once you see your feed, you can close the browser or press Enter here.")
        
        input("Press Enter to close browser and save session...")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()
        print("Session saved. You can now run the scraper.")

if __name__ == "__main__":
    login_linkedin()
