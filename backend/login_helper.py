import os
import time
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def login_and_save():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Use absolute path for settings
    settings_path = os.path.join(base_dir, "settings.json")
    profile_path = os.path.join(base_dir, "chrome-profile")
    
    print(f"Profile path: {profile_path}")
    if not os.path.exists(profile_path):
        os.makedirs(profile_path)
        
    # Options
    options = Options()
    options.add_argument(f"--user-data-dir={profile_path}")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--remote-allow-origins=*")
    
    # Check for manual driver path
    driver_path = None
    if os.path.exists(settings_path):
        try:
            import json
            with open(settings_path, 'r') as f:
                settings = json.load(f)
                driver_path = settings.get("chrome_driver_path")
        except: pass

    service = None
    if driver_path and os.path.exists(driver_path):
        print(f"Using configured driver: {driver_path}")
        service = Service(executable_path=driver_path)
    else:
        print("Using WebDriverManager (Latest)...")
        service = Service(ChromeDriverManager().install())

    try:
        driver = webdriver.Chrome(options=options, service=service)
        driver.get("https://www.linkedin.com/login")
        
        print("\n" + "="*50)
        print("PLEASE LOG IN TO LINKEDIN IN THE BROWSER WINDOW.")
        print("Waiting for you to reach the 'feed' page...")
        print("="*50 + "\n")

        # Wait loop
        start_time = time.time()
        while True:
            try:
                current_url = driver.current_url
                if "feed" in current_url or "dashboard" in current_url:
                    print("\n[SUCCESS] Login detected! Saving session...")
                    time.sleep(5) # Give Chrome time to write cookies
                    driver.quit()
                    print("[DONE] Session saved successfully.")
                    break
                
                if time.time() - start_time > 300: # 5 min timeout
                    print("[TIMEOUT] Login took too long.")
                    driver.quit()
                    break
                
                time.sleep(1)
            except Exception as loop_err:
                print(f"Browser closed? {loop_err}")
                break
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    login_and_save()
