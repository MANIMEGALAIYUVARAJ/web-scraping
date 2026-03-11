from backend.db import mongo, init_db
from flask import Flask
from bson import ObjectId

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev"
init_db(app)

print("=" * 60)
print("RBAC SYSTEM VERIFICATION")
print("=" * 60)

with app.app_context():
    # Get all users
    users = list(mongo.db.users.find({}, {"password": 0}))
    
    print(f"\n📊 Total Users: {len(users)}\n")
    
    for user in users:
        print(f"👤 {user.get('name', 'Unknown')}")
        print(f"   Email: {user.get('email', 'N/A')}")
        print(f"   Role: {user.get('role', 'user').upper()}")
        print(f"   User ID: {user.get('_id')}")
        
        allowed = user.get('allowed_modules', [])
        print(f"   Allowed Modules ({len(allowed)}):")
        
        if user.get('role') == 'admin':
            print(f"      ✅ ADMIN - Full Access to All Modules")
        elif allowed:
            for module in allowed:
                print(f"      ✅ {module}")
        else:
            print(f"      ❌ No modules assigned")
        
        print()
    
    print("=" * 60)
    print("VERIFICATION CHECKLIST")
    print("=" * 60)
    
    # Check admin user
    admin = mongo.db.users.find_one({"email": "manimegalaiyuvaraj38@gmail.com"})
    if admin and admin.get('role') == 'admin':
        print("✅ Admin user configured correctly")
    else:
        print("❌ Admin user not found or role not set")
    
    # Check test users
    test_emails = ["user1@test.com", "user2@test.com", "user3@test.com"]
    for email in test_emails:
        user = mongo.db.users.find_one({"email": email})
        if user:
            print(f"✅ Test user {email} exists")
        else:
            print(f"❌ Test user {email} not found")
    
    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("=" * 60)
    print("1. Refresh your browser at http://localhost:5173")
    print("2. Login with your admin account")
    print("3. Verify 'Admin Panel' appears in sidebar")
    print("4. Click 'User Management' to see all users")
    print("5. Follow the testing guide for complete verification")
    print("=" * 60)
