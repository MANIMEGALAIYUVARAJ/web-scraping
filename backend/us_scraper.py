import sys
import os
sys.path.append(os.path.dirname(__file__))
from money2020_scraper import Money2020Scraper
from financial_brand_forum_scraper import FinancialBrandForumScraper

def main(query=None, limit=10):
    all_data = []
    
    # 1. Money20/20 USA
    # Use half the limit for each if multiple sites, or just greedy
    try:
        print("Starting Money20/20 USA Scraper...")
        m_scraper = Money2020Scraper(region='US', site_name='Money2020 USA', base_url='https://usa.money2020.com/speakers')
        m_data = m_scraper.scrape(query=query, limit=limit)
        if m_data: all_data.extend(m_data)
    except Exception as e:
        print(f"Failed to run Money2020 USA: {e}")

    # 2. Financial Brand Forum
    if len(all_data) < limit:
        try:
            print("Starting Financial Brand Forum Scraper...")
            f_limit = limit - len(all_data)
            fb_scraper = FinancialBrandForumScraper()
            fb_data = fb_scraper.scrape(query=query, limit=f_limit)
            if fb_data: all_data.extend(fb_data)
        except Exception as e:
            print(f"Failed to run Financial Brand Forum: {e}")

    return all_data[:limit]

if __name__ == "__main__":
    import json
    results = main(query="CEO", limit=5)
    print(f"Scraped {len(results)} total US speakers.")
    print(json.dumps(results, indent=2))
