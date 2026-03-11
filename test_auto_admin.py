"""
Test script to verify auto-admin first user functionality.
This will clear all users and test that the first registered user becomes admin.
"""
from backend.db import mongo, init_db, is_first_user
from flask import Flask

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev"
init_db(app)

print("=" * 60)
print("AUTO-ADMIN FIRST USER TEST")
print("=" * 60)

with app.app_context():
    # Show current user count
    user_count = mongo.db.users.count_documents({})
    print(f"\n📊 Current user count: {user_count}")
    
    # Test is_first_user function
    first = is_first_user()
    print(f"🔍 is_first_user() returns: {first}")
    
    if user_count > 0:
        print("\n⚠️  Database already has users.")
        print("To test auto-admin functionality:")
        print("1. Backup your current users if needed")
        print("2. Clear the users collection: mongo.db.users.delete_many({})")
        print("3. Register a new user through the frontend")
        print("4. Verify they get admin role automatically")
        
        # Show first user in database
        first_user = mongo.db.users.find_one({}, sort=[("createdAt", 1)])
        if first_user:
            print(f"\n📋 First user in database:")
            print(f"   Name: {first_user.get('name')}")
            print(f"   Email: {first_user.get('email')}")
            print(f"   Role: {first_user.get('role')}")
            print(f"   Created: {first_user.get('createdAt')}")
    else:
        print("\n✅ Database is empty - ready for auto-admin test!")
        print("\nNext steps:")
        print("1. Go to http://localhost:5173")
        print("2. Register a new user")
        print("3. That user will automatically become admin")
        print("4. Subsequent users will be regular users")

print("\n" + "=" * 60)
print("HOW AUTO-ADMIN WORKS")
print("=" * 60)
print("✓ When a user registers, system checks if database is empty")
print("✓ If empty (first user), role = 'admin'")
print("✓ If not empty, role = 'user'")
print("✓ First user gets full access to all modules")
print("=" * 60)
