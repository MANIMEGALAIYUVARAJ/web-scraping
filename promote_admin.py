from backend.db import mongo, init_db
from flask import Flask
import os

app = Flask(__name__)
# Use a valid secret key
app.config["SECRET_KEY"] = "dev" 
init_db(app)

admin_email = "manimegalaiyuvaraj38@gmail.com"

with app.app_context():
    user = mongo.db.users.find_one({"email": admin_email})
    if user:
        mongo.db.users.update_one(
            {"email": admin_email},
            {"$set": {"role": "admin"}}
        )
        print(f"Successfully promoted {admin_email} to admin.")
    else:
        print(f"User {admin_email} not found. Please register this user first or I can create it.")
