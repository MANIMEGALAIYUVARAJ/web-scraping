import sys
import os
import time

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    from driver_utils import get_driver, kill_orphaned_chrome
    from linkedinjob_scraper import scrape_linkedin_jobs
except ImportError:
    # Handle running from root or backend
    sys.path.append(os.getcwd())
    from driver_utils import get_driver, kill_orphaned_chrome
    from linkedinjob_scraper import scrape_linkedin_jobs

def verify():
    print("--- STARTING VERIFICATION ---")
    
    # 1. Test Driver Initialization (should trigger cleanup if locked)
    print("\n1. Testing Driver Initialization...")
    try:
        # Use a dummy profile path to trigger the persistent profile logic
        profile_path = os.path.abspath("backend/chrome-profile")
        if not os.path.exists(profile_path):
            os.makedirs(profile_path)
            
        driver = get_driver(headless=True, profile_path=profile_path)
        print("[SUCCESS] Driver initialized successfully!")
        driver.quit()
    except Exception as e:
        print(f"[FAILED] Driver initialization FAILED: {e}")
        import traceback
        traceback.print_exc()
        return

    # 2. Test Scraper (Guest Mode Check)
    print("\n2. Testing LinkedIn Jobs Scraper (Guest Mode)...")
    try:
        # We expect this to use the fallback logic if the profile is locked/borked
        # Or just work if the profile is clean.
        # Queries for 'python' usually have results.
        results = scrape_linkedin_jobs("python", limit=3, debug=True)
        
        if len(results) > 0:
            print(f"[SUCCESS] Scraper SUCCESS! Found {len(results)} jobs.")
            print("First job sample:", results[0])
        else:
            print("[WARNING] Scraper ran but found 0 jobs. Guest mode selectors might need tuning or IP is blocked.")
            
    except Exception as e:
        print(f"[FAILED] Scraper FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify()
