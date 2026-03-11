
from backend.db import mongo, init_db, make_admin
from flask import Flask
import sys

app = Flask(__name__)
# Use the same URI as in db.py
app.config["MONGO_URI"] = "mongodb://127.0.0.1:27017/scraper_db"
init_db(app)

def promote_to_admin(email):
    with app.app_context():
        user = mongo.db.users.find_one({"email": email})
        if not user:
            print(f"User with email {email} not found.")
            return
        
        make_admin(email)
        print(f"User {email} is now an Admin.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python create_admin.py <email>")
    else:
        promote_to_admin(sys.argv[1])
