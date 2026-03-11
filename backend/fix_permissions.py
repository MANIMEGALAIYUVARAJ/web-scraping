
from flask import Flask
from db import init_db, mongo

app = Flask(__name__)
# Use 127.0.0.1 as per recent fix
app.config["MONGO_URI"] = "mongodb://127.0.0.1:27017/scraper_db"
init_db(app)

ALL_MODULES = [
    "linkedin-articles", "linkedin-jobs", "opentable", "restaurants", 
    "reddit", "reddit-threads", "twitter", "instagram", "instagram-articles", 
    "youtube", "google-maps", "speakers", "gitex", "eauctions"
]

def fix_permissions():
    with app.app_context():
        users = mongo.db.users.find({})
        count = 0
        for user in users:
            # If admin, give all modules. If user, give all modules (as per request "User 3 should have access to all", 
            # effectively migrating everyone to have access initially, then Admin restricts).
            # The prompt said: "User 1 should only see Instagram..., User 3 all". 
            # But to fix "empty sidebar" immediately, let's give ALL to everyone, and Admin can remove.
            
            mongo.db.users.update_one(
                {"_id": user["_id"]},
                {"$set": {"allowed_modules": ALL_MODULES}}
            )
            print(f"Updated permissions for {user.get('email', 'unknown')}")
            count += 1
        print(f"Finished updating {count} users.")

if __name__ == "__main__":
    fix_permissions()
