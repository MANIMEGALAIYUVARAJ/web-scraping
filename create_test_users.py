from backend.db import mongo, init_db, create_user, get_user_by_email
from flask import Flask

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev"
init_db(app)

# Test user configurations matching the requirements
test_users = [
    {
        "name": "User One",
        "email": "user1@test.com",
        "password": "password123",
        "allowed_modules": ["instagram", "instagram-articles", "twitter"]
    },
    {
        "name": "User Two", 
        "email": "user2@test.com",
        "password": "password123",
        "allowed_modules": ["linkedin-articles", "linkedin-jobs"]
    },
    {
        "name": "User Three",
        "email": "user3@test.com",
        "password": "password123",
        "allowed_modules": [
            "linkedin-articles", "linkedin-jobs", "opentable", "restaurants",
            "reddit", "reddit-threads", "twitter", "instagram", "instagram-articles",
            "youtube", "google-maps", "speakers", "gitex", "eauctions"
        ]
    }
]

with app.app_context():
    for user_data in test_users:
        existing = get_user_by_email(user_data["email"])
        if existing:
            # Update permissions if user exists
            mongo.db.users.update_one(
                {"email": user_data["email"]},
                {"$set": {"allowed_modules": user_data["allowed_modules"]}}
            )
            print(f"✓ Updated permissions for {user_data['email']}")
        else:
            # Create new user
            create_user(
                name=user_data["name"],
                email=user_data["email"],
                password=user_data["password"],
                role="user",
                allowed_modules=user_data["allowed_modules"]
            )
            print(f"✓ Created user {user_data['email']}")
    
    print("\n=== Test Users Created ===")
    print("User 1: user1@test.com (Instagram + Twitter only)")
    print("User 2: user2@test.com (LinkedIn only)")
    print("User 3: user3@test.com (All modules)")
    print("Password for all: password123")
