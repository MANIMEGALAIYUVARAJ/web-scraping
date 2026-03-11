from money2020_scraper import main as scrape_europe
results = scrape_europe(query="CEO", limit=1, debug=True)
if results:
    r = results[0]
    print(f"Name: {r.get('Name')}")
    print(f"Keys found: {list(r.keys())}")
    print(f"Bio preview: {r.get('Bio', 'MISSING')[:100]}...")
    print(f"LinkedIn: {r.get('LinkedIn')}")
else:
    print("No results returned.")
