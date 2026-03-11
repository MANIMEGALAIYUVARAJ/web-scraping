from flask_pymongo import PyMongo
from datetime import datetime
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

mongo = PyMongo()

def init_db(app):
    # Configure MongoDB URI - using default local instance if not provided
    app.config["MONGO_URI"] = "mongodb://127.0.0.1:27017/scraper_db"
    mongo.init_app(app)

def get_user_by_email(email):
    return mongo.db.users.find_one({"email": email})

def is_first_user():
    """Check if this is the first user in the system"""
    return mongo.db.users.count_documents({}) == 0

def create_user(name, email, password, role="user", allowed_modules=None):
    if allowed_modules is None:
        # Default modules for public registration - maybe all for now?
        allowed_modules = ["linkedin-articles", "linkedin-jobs", "twitter", "reddit", "instagram", "youtube", "google-maps", "speakers", "gitex", "eauctions", "restaurants", "opentable"]
        
    user = {
        "name": name,
        "email": email,
        "password": generate_password_hash(password),
        "createdAt": datetime.now(),
        "role": role, 
        "allowed_modules": allowed_modules,
        "settings": {
            "theme": "dark",
            "notifications": True
        }
    }
    result = mongo.db.users.insert_one(user)
    return str(result.inserted_id)

def verify_user(email, password):
    user = get_user_by_email(email)
    if user and check_password_hash(user["password"], password):
        return user
    return None

def get_user_settings(user_id):
    try:
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        return user.get("settings", {}) if user else {}
    except:
        return {}

def update_user_settings(user_id, settings):
    try:
        mongo.db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"settings": settings}}
        )
        return True
    except:
        return False

def get_history_by_user(user_id):
    try:
        # Convert string ID to ObjectId if needed, though we store strings usually for simplicity in JSON APIs
        # But Mongo uses ObjectIds. Let's try to handle both.
        # Ideally we store userId as string in history to avoid ObjectId headaches, 
        # or we cast when querying.
        history = list(mongo.db.scrapeHistories.find({"userId": user_id}).sort("createdAt", -1))
        # Convert ObjectIds to strings for JSON serialization
        for h in history:
            h["_id"] = str(h["_id"])
        return history
    except Exception as e:
        print(f"Error fetching history: {e}")
        return []

def log_history_to_db(user_id, platform, query, count, csv_path):
    if not user_id:
        return # Cannot save without user
        
    record = {
        "userId": user_id,
        "scraper": platform,
        "query": query,
        "items": count,
        "csv_path": csv_path,
        "createdAt": datetime.now(),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"), # Keep for compatibility
        "status": "Completed"
    }
    mongo.db.scrapeHistories.insert_one(record)

def get_all_users():
    users = list(mongo.db.users.find({}, {"password": 0})) # Exclude password
    for u in users:
        u["_id"] = str(u["_id"])
    return users

def update_user_permissions(user_id, allowed_modules):
    try:
        mongo.db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"allowed_modules": allowed_modules}}
        )
        return True
    except:
        return False

def make_admin(email):
    mongo.db.users.update_one(
        {"email": email},
        {"$set": {"role": "admin"}}
    )

def update_user_profile_photo(user_id, photo_url):
    try:
        mongo.db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"profile_photo": photo_url}}
        )
        return True
    except:
        return False

