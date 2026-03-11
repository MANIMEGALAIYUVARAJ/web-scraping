import os
import json
import logging
import uuid
import shutil
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")

def load_settings():
    """Load settings from the JSON file."""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
    else:
        logger.warning(f"Settings file not found at: {SETTINGS_FILE}")
    return {}

def get_driver(headless=True, profile_path=None):
    """
    Simplified get_driver that matches force_login.py logic for persistent profiles.
    """
    settings = load_settings()
    chrome_driver_path = settings.get("chrome_driver_path", "").strip()

    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--remote-allow-origins=*")
    
    # Headless handling (Actually Hidden Headful to avoid detection)
    # Headless handling (Actually Hidden Headful to avoid detection)
    # We use start-maximized for BOTH to ensure correct desktop layout
    options.add_argument("--start-maximized")
    
    if headless:
        # We will minimize the window after creation
        pass

    # Profile handling
    import tempfile
    if profile_path:
        if not os.path.exists(profile_path):
            os.makedirs(profile_path)
        options.add_argument(f"--user-data-dir={profile_path}")
        logger.info(f"Using persistent profile at: {profile_path}")
    else:
        # Temporary profile logic
        base_profile_dir = os.path.abspath("temp_profiles")
        os.makedirs(base_profile_dir, exist_ok=True)
        temp_dir_obj = tempfile.TemporaryDirectory(dir=base_profile_dir, prefix="profile_")
        options.add_argument(f"--user-data-dir={temp_dir_obj.name}")

    # Service / Driver Resolution
    service = None
    if chrome_driver_path and os.path.exists(chrome_driver_path):
        logger.info(f"Using manual ChromeDriver path: {chrome_driver_path}")
        service = Service(executable_path=chrome_driver_path)
    else:
        logger.info("Using WebdriverManager (latest)")
        from webdriver_manager.chrome import ChromeDriverManager
        try:
            driver_path = ChromeDriverManager().install()
            service = Service(executable_path=driver_path)
        except Exception as e:
            logger.error(f"WDM failed: {e}")
            raise e

    # Attempt Initialization
    try:
        # Proactive cleanup for persistent profiles to match force_login.py success
        if profile_path:
            logger.info("Proactive cleanup of Chrome processes/locks...")
            kill_orphaned_chrome()
            clean_profile_locks(profile_path)

        driver = webdriver.Chrome(options=options, service=service)
        
        # Attach temp dir manager to keep it alive if needed
        if not profile_path and 'temp_dir_obj' in locals():
            driver._temp_dir_mgr = temp_dir_obj

        # Basic Stealth
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })
        
        # NOTE: We cannot use headless or minimized mode for LinkedIn as it triggers detection/rendering issues.
        # We force visible mode for reliability.
        if headless:
            logger.warning("Headless mode forced to VISIBLE for LinkedIn reliability.")

        return driver

    except Exception as e:
        logger.warning(f"Preferred driver init failed: {e}")
        try:
            with open("driver_error.log", "a") as f: f.write(f"Init Error: {e}\n")
        except: pass
        
        # Retry logic (if proactive cleanup failed or wasn't enough? or maybe just retry)
        # Since we already cleaned up, maybe retry is futile, but let's try once more
        if profile_path:
            try:
                logger.info("Retrying driver init...")
                time.sleep(2) # Wait a bit more
                driver = webdriver.Chrome(options=options, service=service)
                driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                    "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
                })
                return driver
            except Exception as retry_err:
                logger.error(f"Retry failed: {retry_err}")
                try:
                    with open("driver_error.log", "a") as f: f.write(f"Retry Error: {retry_err}\n")
                except: pass
                # Fall through to guest mode

        logger.warning("Falling back to Guest Mode (Temporary Profile)...")
        # GUEST MODE FALLBACK
        fallback_options = Options()
        if headless:
            fallback_options.add_argument("--headless=new")
            fallback_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        else:
            fallback_options.add_argument("--start-maximized")
        
        fallback_options.add_argument("--disable-gpu")
        fallback_options.add_argument("--no-sandbox")
        fallback_options.add_argument("--disable-dev-shm-usage")
        fallback_options.add_argument("--remote-allow-origins=*")
        fallback_options.add_argument("--disable-blink-features=AutomationControlled")

        fallback_base = os.path.abspath("temp_fallback_profiles")
        os.makedirs(fallback_base, exist_ok=True)
        fallback_temp = tempfile.TemporaryDirectory(dir=fallback_base, prefix="fallback_")
        fallback_options.add_argument(f"--user-data-dir={fallback_temp.name}")
        
        driver = webdriver.Chrome(options=fallback_options, service=service)
        driver._temp_dir_mgr = fallback_temp
        
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })
        return driver

def kill_orphaned_chrome():
    """Kills any chrome.exe or chromedriver.exe processes to free up locks."""
    import subprocess
    try:
        if os.name == 'nt':
            subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["taskkill", "/F", "/IM", "chromedriver.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(1) # Wait for release
    except Exception as e:
        logger.warning(f"Failed to kill chrome processes: {e}")

def clean_profile_locks(profile_path):
    """Removes lock files from the User Data directory."""
    if not os.path.exists(profile_path):
        return
        
    lock_files = ["SingletonLock", "SingletonCookie", "SingletonSocket", "Lockfile"]
    for filename in lock_files:
        path = os.path.join(profile_path, filename)
        if os.path.exists(path):
            try:
                os.remove(path)
                logger.info(f"Removed lock file: {path}")
            except Exception as e:
                logger.warning(f"Could not remove {path}: {e}")


def install_configured_driver(version_key):
    """
    Installs the driver for the given version key (e.g., 'stable', '144') 
    and returns the absolute path.
    """
    # Shared map - keep this updated or move to a constant
    version_map = {
        "stable": "145.0.7632.26",
        "beta": "146.0.7655.0",
        "dev": "146.0.7655.0",
        "canary": "146.0.7665.0",
        "144": "144.0.7559.110"
    }
    
    target_version = version_map.get(version_key.lower(), version_key)
    
    try:
        if not target_version or target_version.lower() == "latest":
             print("Installing latest/matching driver...")
             path = ChromeDriverManager().install()
        else:
             print(f"Installing specific driver version: {target_version}...")
             path = ChromeDriverManager(driver_version=target_version).install()
             
        # Normalize path
        path = os.path.abspath(path)
        
        # Update settings with this new path
        settings = load_settings()
        settings["chrome_driver_path"] = path
        settings["chrome_version"] = version_key
        
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=2)
            
        return path
    except Exception as e:
        logger.error(f"Failed to install driver: {e}")
        raise e
