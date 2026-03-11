import os
import time
import shutil
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def kill_chrome():
    print("Killing orphaned Chrome processes...")
    try:
        if os.name == 'nt':
            subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["taskkill", "/F", "/IM", "chromedriver.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"Error killing chrome: {e}")
    time.sleep(2)

def clean_locks(profile_path):
    print(f"Cleaning locks in {profile_path}...")
    lock_files = ["SingletonLock", "SingletonCookie", "SingletonSocket", "Lockfile"]
    for filename in lock_files:
        path = os.path.join(profile_path, filename)
        if os.path.exists(path):
            try:
                os.remove(path)
                print(f"Removed {path}")
            except Exception as e:
                print(f"Failed to remove {path}: {e}")

def force_login():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    profile_path = os.path.join(base_dir, "chrome-profile")
    
    if not os.path.exists(profile_path):
        os.makedirs(profile_path)
        
    kill_chrome()
    clean_locks(profile_path)
    
    print(f"Attempting to open Chrome with profile: {profile_path}")
    
    options = Options()
    options.add_argument(f"--user-data-dir={profile_path}")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--remote-allow-origins=*")
    
    # Attempt to load settings for driver path, else use WDM
    driver_path = None
    try:
        import json
        settings_path = os.path.join(base_dir, "settings.json")
        if os.path.exists(settings_path):
            with open(settings_path, 'r') as f:
                settings = json.load(f)
                driver_path = settings.get("chrome_driver_path")
    except:
        pass

    service = None
    if driver_path and os.path.exists(driver_path):
        print(f"Using configured driver: {driver_path}")
        service = Service(executable_path=driver_path)
    else:
        print("Using WebDriverManager...")
        from webdriver_manager.chrome import ChromeDriverManager
        service = Service(ChromeDriverManager().install())

    try:
        driver = webdriver.Chrome(options=options, service=service)
        driver.get("https://www.linkedin.com/login")
        print("\nSUCCESS! Chrome opened.")
        print("Please log in, wait for feed, then press Enter inside this terminal.")
        input("Press Enter to close and save...")
        driver.quit()
        print("Session saved.")
    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    force_login()
