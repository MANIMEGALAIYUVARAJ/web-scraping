import sys
import os
import time

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    from linkedinarticles import scrape_linkedin_articles
except ImportError:
    sys.path.append(os.getcwd())
    from linkedinarticles import scrape_linkedin_articles

def verify_articles():
    log_file = "verify_status.log"
    with open(log_file, "w", encoding="utf-8") as f:
        f.write("--- VERIFYING LINKEDIN ARTICLES ---\n")
        try:
            f.write("[INFO] Starting scrape for 'AI' (limit=3)...\n")
            # Set debug=False for HIDDEN HEADFUL execution to test if profile works
            results = scrape_linkedin_articles("AI", limit=3, debug=False)
            
            if results:
                f.write(f"[SUCCESS] Found {len(results)} articles.\n")
                f.write(f"Sample: {results[0]}\n")
            else:
                f.write("[WARNING] Scrape completed but returned 0 results. Check filters or selectors.\n")
                # Save page source for debugging
                try:
                    from driver_utils import get_driver
                    # NOTE: We can't easily access the driver here to dump source unless we modify scrape_linkedin_articles 
                    # OR we run the scrape steps manually here. 
                    # For now, we rely on the fact that scrape_linkedin_articles takes a screenshot on failure.
                except: pass
                
        except RuntimeError as re:
            f.write(f"[FAILED] Login Check Failed: {re}\n")
        except Exception as e:
            import traceback
            f.write(f"[FAILED] Unexpected Error: {e}\n")
            f.write(traceback.format_exc())

if __name__ == "__main__":
    verify_articles()
