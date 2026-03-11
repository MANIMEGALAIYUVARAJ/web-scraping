import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from leading_authorities_scraper import main

print("Running Leading Authorities Smoke Test...")
query = "CEO"
limit = 1
results = main(query=query, limit=limit)

print("\n--- RESULTS ---")
print(f"Count: {len(results)}")
if len(results) > 0:
    for i, res in enumerate(results):
        print(f"Result {i+1}:")
        print(f"  Name: {res.get('Name')}")
        print(f"  Role: {res.get('Role')}")
        print(f"  Source URL: {res.get('Source URL')}")
        
        # Check relevance
        searchable = f"{res.get('Name')} {res.get('Role')} {res.get('Bio', '')}".lower()
        if query.lower() in searchable:
            print("  Relevance: OK")
        else:
            print("  Relevance: FAILED (Query not found in searchable text)")
else:
    print("No results found.")

if len(results) == limit:
    print("\nLimit Enforcement: OK")
else:
    print(f"\nLimit Enforcement: FAILED (Expected {limit}, got {len(results)})")
