from opentable_restaurant import scrape_opentable
import json

def debug_run():
    print("Starting debug run...")
    results = scrape_opentable("us", "new york", limit=10, headless=False)
    print(f"Debug run complete. Found {len(results)} items.")
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    debug_run()
