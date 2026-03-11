import sys
import os
sys.path.append(os.path.dirname(__file__))
from base_scraper import GenericEmailListScraper
from kruger_cowne_scraper import KrugerCowneScraper

def main(query=None, limit=10):
    all_data = []
    
    # 1. Kruger Cowne (Specialized)
    try:
        print("Starting Kruger Cowne Scraper...")
        k_scraper = KrugerCowneScraper()
        k_data = k_scraper.scrape(query=query, limit=limit)
        if k_data: all_data.extend(k_data)
    except Exception as e:
        print(f"Failed to run Kruger Cowne: {e}")

    # 2. IA Annual Conference (Generic fallback if limit not reached)
    if len(all_data) < limit:
        try:
            print("Starting IA Annual Conference Scraper...")
            f_limit = limit - len(all_data)
            g_scraper = GenericEmailListScraper('UK', 'IA Annual Conference', 'https://theiaengine.com/speakers')
            g_data = g_scraper.scrape() # This one doesn't support query yet natively in base
            if g_data:
                # Add minimal query filter if needed
                if query:
                    g_data = [d for d in g_data if query.lower() in str(d).lower()]
                all_data.extend(g_data[:f_limit])
        except Exception as e:
            print(f"Failed to run IA Annual Conference: {e}")

    return all_data[:limit]

if __name__ == "__main__":
    import json
    results = main(query="Finance", limit=3)
    print(json.dumps(results, indent=2))
