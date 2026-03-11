from eauctionsindia import scrape_eauctionsindia
import time

try:
    print("Starting e-auctions scraper verification...")
    # Scrape just 1 item to verify startup
    generator = scrape_eauctionsindia("Chennai", limit=1)
    for row in generator:
        print(f"Scraped: {row.get('url')}")
    print("Verification finished successfully.")
except Exception as e:
    print(f"Verification failed: {e}")
