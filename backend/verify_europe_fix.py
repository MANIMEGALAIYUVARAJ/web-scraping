import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from europe_scraper import main as scrape_europe
    
    print("Running Europe Scraper Test with query='CEO' and limit=2...")
    results = scrape_europe(query="CEO", limit=2, debug=True)
    
    print(f"\nResults count: {len(results)}")
    for i, res in enumerate(results, 1):
        print(f"\nResult {i}:")
        print(f"  Name: {res.get('Name')}")
        print(f"  Role: {res.get('Role/Designation')}")
        print(f"  Bio: {res.get('Description', '')[:100]}...")
        print(f"  LinkedIn: {res.get('LinkedIn')}")
        
    if len(results) > 0:
        print("\n✅ Verification SUCCESS: Scraper returned data.")
    else:
        print("\n❌ Verification FAILED: No data returned. (This might be due to driver issues in this environment)")
        
except Exception as e:
    print(f"\n❌ Error during verification: {e}")
    import traceback
    traceback.print_exc()
