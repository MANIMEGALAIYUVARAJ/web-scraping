from base_scraper import GenericEmailListScraper

from money2020_scraper import main as scrape_money2020

def main(query=None, limit=10, debug=False):
    try:
        data = scrape_money2020(query=query, limit=limit, debug=debug)
        return data
    except Exception as e:
        print(f"Failed to run Europe scraper: {e}")
        return []

if __name__ == "__main__":
    main()
