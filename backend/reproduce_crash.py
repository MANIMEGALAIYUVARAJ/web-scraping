from driver_utils import get_driver
import time

try:
    print("Attempting to initialize driver...")
    driver = get_driver(headless=False)
    print("Driver initialized successfully!")
    driver.get("https://www.google.com")
    time.sleep(5)
    driver.quit()
    print("Driver quit successfully.")
except Exception as e:
    print(f"Driver initialization failed: {e}")
