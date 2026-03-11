import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from linkedinarticles import scrape_linkedin_articles
from linkedinjob_scraper import scrape_linkedin_jobs

def main():
    print("=== LinkedIn Scraper Verification ===")
    print("1. Verify LinkedIn Articles Scraper")
    print("2. Verify LinkedIn Jobs Scraper")
    print("3. Exit")
    
    choice = input("Select an option (1-3): ").strip()
    
    if choice == "3":
        return

    term = input("Enter search term (default 'AI'): ").strip() or "AI"
    limit = int(input("Enter limit (default 3): ").strip() or 3)
    
    print("\nStarting scraper in DEBUG mode...")
    print("A browser window will open. Please check if you are logged in.")
    print("If not logged in, please log in manually in that window.")
    print("---------------------------------------------------------")

    try:
        if choice == "1":
            results = scrape_linkedin_articles(term, limit=limit, debug=True)
            print(f"\nScraped {len(results)} articles.")
            for r in results:
                print(f"- {r.get('author', 'Unknown')}: {r.get('post_text', '')[:50]}...")
                
        elif choice == "2":
            results = scrape_linkedin_jobs(term, limit=limit, save_csv=False, debug=True)
            print(f"\nScraped {len(results)} jobs.")
            for r in results:
                print(f"- {r.get('job_title', 'Unknown')} at {r.get('company_name', 'Unknown')}")
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
