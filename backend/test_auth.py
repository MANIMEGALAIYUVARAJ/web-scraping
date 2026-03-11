import json
import unittest
import sys
from app import app
from db import mongo

class TestAuthIsolation(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["MONGO_URI"] = "mongodb://localhost:27017/scraper_db_test"
        self.client = app.test_client()
        self.ctx = app.app_context()
        self.ctx.push()
        
        # Clean db before tests
        try:
            mongo.db.users.delete_many({})
            mongo.db.scrapeHistories.delete_many({})
        except:
            pass

    def tearDown(self):
        # We could clean up, but keeping data for inspection is sometimes useful
        # self.ctx.pop() # causes issues sometimes if not careful, but ok here
        pass

    def test_auth_flow_and_isolation(self):
        client = self.client
        
        # 1. Register/Login New User A
        print("\n[Test] Registering User A...")
        res = client.post("/api/login", json={
            "email": "alice@example.com",
            "password": "password123",
            "name": "Alice"
        })
        self.assertEqual(res.status_code, 200)
        data_a = res.get_json()
        self.assertEqual(data_a["status"], "created")
        user_id_a = data_a["userId"]
        self.assertEqual(data_a["name"], "Alice")
        self.assertEqual(data_a["history"], [])

        # 2. Login again (should exist)
        print("[Test] Logging in User A...")
        res = client.post("/api/login", json={
            "email": "alice@example.com",
            "password": "password123"
        })
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["status"], "exists")
        self.assertEqual(res.get_json()["userId"], user_id_a)

        # 3. Invalid Password
        print("[Test] Testing Bad Password...")
        res = client.post("/api/login", json={
            "email": "alice@example.com",
            "password": "wrongpassword"
        })
        self.assertEqual(res.status_code, 401)

        # 4. Add History for User A
        print("[Test] Adding history for User A...")
        from db import log_history_to_db
        log_history_to_db(user_id_a, "manual_test", "test query", 10, "/tmp/test.csv")
        
        # 5. Check User A History
        print("[Test] Checking User A History...")
        res = client.get(f"/api/history?userId={user_id_a}")
        history = res.get_json()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["scraper"], "manual_test")

        # 6. Register/Login User B
        print("[Test] Registering User B...")
        res = client.post("/api/login", json={
            "email": "bob@example.com",
            "password": "password456",
            "name": "Bob"
        })
        self.assertEqual(res.status_code, 200)
        data_b = res.get_json()
        user_id_b = data_b["userId"]
        
        # 7. Check User B History (Should be EMPTY)
        print("[Test] Checking User B History (Should be empty)...")
        res = client.get(f"/api/history?userId={user_id_b}")
        history_b = res.get_json()
        self.assertEqual(len(history_b), 0)
        
        # 8. Check User A History Again (Should still be there)
        res = client.get(f"/api/history?userId={user_id_a}")
        self.assertEqual(len(res.get_json()), 1)
        
        # 9. Settings Isolation
        print("[Test] Testing Settings Isolation...")
        client.post("/api/settings", json={"userId": user_id_a, "theme": "light"})
        client.post("/api/settings", json={"userId": user_id_b, "theme": "dark"})
        
        res_a = client.get(f"/api/settings?userId={user_id_a}")
        self.assertEqual(res_a.get_json()["theme"], "light")
        
        res_b = client.get(f"/api/settings?userId={user_id_b}")
        self.assertEqual(res_b.get_json()["theme"], "dark")

        print("\n[SUCCESS] All authentication and isolation tests passed!")

if __name__ == "__main__":
    unittest.main()
