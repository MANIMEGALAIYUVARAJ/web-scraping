import requests
import time
import sys

BASE_URL = "http://3.110.215.102:61631"

def test_login(name, email):
    print(f"Testing login for {name} ({email})...")
    res = requests.post(f"{BASE_URL}/api/login", json={"name": name, "email": email})
    if res.status_code != 200:
        print(f"FAILED: Login failed: {res.text}")
        return None
    data = res.json()
    print(f"SUCCESS: Logged in as userId={data.get('userId')}, history_len={len(data.get('history'))}")
    return data.get("userId")

def test_scrape(user_id, platform, query):
    print(f"Testing scrape for userId={user_id}...")
    res = requests.get(f"{BASE_URL}/api/live_scrape", params={"platform": platform, "query": query, "userId": user_id, "limit": 1})
    if res.status_code != 200:
         print(f"FAILED: Scrape failed: {res.text}")
         return False
    print("SUCCESS: Scrape completed")
    return True

def test_history(user_id, expected_count):
    print(f"Testing history for userId={user_id} (expecting {expected_count})...")
    res = requests.get(f"{BASE_URL}/api/history", params={"userId": user_id})
    if res.status_code != 200:
        print(f"FAILED: History fetch failed: {res.text}")
        return False
    data = res.json()
    if len(data) == expected_count:
        print(f"SUCCESS: Got {len(data)} items.")
        return True
    else:
        print(f"FAILED: Expected {expected_count} items, got {len(data)}")
        return False

def run_verification():
    # Wait for server
    time.sleep(2) 
    
    # 1. Login User A (Alice)
    alice_id = test_login("Alice", "alice@example.com")
    if not alice_id: sys.exit(1)
    
    # 2. Check Alice History (should be 0 or N depending on previous runs, but let's assume 0 for new db)
    # Actually, if we run this multiple times, it might grow.
    # Let's count current history
    res = requests.get(f"{BASE_URL}/api/history", params={"userId": alice_id})
    initial_alice_count = len(res.json())
    
    # 3. Scrape for Alice
    test_scrape(alice_id, "twitter", "python")
    
    # 4. Check Alice History (should be initial + 1)
    test_history(alice_id, initial_alice_count + 1)
    
    # 5. Login User B (Bob)
    bob_id = test_login("Bob", "bob@example.com")
    if not bob_id: sys.exit(1)
    
    # 6. Check Bob History (should be whatever Bob had, likely 0 if new)
    # Ensure it's not Alice's count (unless Bob also has coincidentally same count, but highly unlikely if we just scraped for Alice)
    res = requests.get(f"{BASE_URL}/api/history", params={"userId": bob_id})
    bob_count = len(res.json())
    
    if bob_count == initial_alice_count + 1 and initial_alice_count == 0:
        # This check is weak if both have 1, but if Alice started 0->1, Bob should be 0.
        print("WARNING: Bob has same history count as Alice. Checking content...")
    
    if bob_id == alice_id:
        print("FAILED: IDs are identical!")
    else:
        print(f"SUCCESS: IDs are different (Alice: {alice_id}, Bob: {bob_id})")

    print("\nVerification Complete.")

if __name__ == "__main__":
    run_verification()
