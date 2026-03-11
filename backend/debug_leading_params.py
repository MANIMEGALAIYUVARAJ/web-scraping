import os
import time
from DrissionPage import ChromiumPage, ChromiumOptions

def debug_leading_authorities():
    co = ChromiumOptions()
    co.set_argument('--no-sandbox')
    co.set_argument('--disable-gpu')
    page = ChromiumPage(co)
    
    # Try different search parameters
    test_params = ["search", "keys", "keyword", "q", "query", "search_api_fulltext"]
    query = "CEO"
    base_url = "https://www.leadingauthorities.com/uk/speaker-search"
    
    found_param = None
    
    for param in test_params:
        test_url = f"{base_url}?{param}={query}"
        print(f"Testing URL: {test_url}")
        page.get(test_url)
        time.sleep(5)
        
        # Check for Cloudflare
        if "Just a moment" in page.title:
            print(f"  Cloudflare detected on {param}. Waiting...")
            time.sleep(10)
            
        # Check for items
        items = page.eles('css:.speaker-grid--item')
        if items:
            print(f"  SUCCESS! Found {len(items)} items using param '{param}'")
            found_param = param
            # Take a screenshot or save HTML for verification
            with open(f"debug_leading_{param}.html", "w", encoding="utf-8") as f:
                f.write(page.html)
            break
        else:
            print(f"  No items found for param '{param}'.")
            
    if not found_param:
        print("Failed to find any working search parameter.")
        # Save HTML for the first attempt to see what's on the page
        with open("debug_leading_failed.html", "w", encoding="utf-8") as f:
            f.write(page.html)

    page.quit()

if __name__ == "__main__":
    debug_leading_authorities()
