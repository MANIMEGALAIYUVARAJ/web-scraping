import os
import csv
import traceback
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS

from instagram_scraper import scrape_instagram
from linkedinarticles import scrape_linkedin_articles
from linkedinjob_scraper import scrape_linkedin_jobs
from twitter_scraper import scrape_twitter
from reddit import scrape_reddit
from speakers_scraper import scrape_speakers
from gitex_speakers import scrape_gitex_speakers
from gmap_scraper import scrape_gmap
from eauctionsindia import scrape_eauctionsindia
from restaurant_scraper import scrape_restaurant
from opentable_restaurant import scrape_opentable
from youtube_scraper import scrape_youtube
from instagramarticles import scrape_instagram_hashtag
from thread_reddit import scrape_thread_reddit
from bharat_2025_scraper import main as scrape_bharat_2025
from bharat_fintech_scraper import main as scrape_bharat_fintech
from europe_scraper import main as scrape_europe
from fof_scraper import main as scrape_fof
from gartner_scraper import main as scrape_gartner
from india_scraper import main as scrape_india
from indian_speaker_bureau_scraper import main as scrape_isb
from leading_authorities_scraper import main as scrape_leading_authorities
from london_scraper import main as scrape_london
from london_speaker_bureau_scraper import main as scrape_lsb
from nexgen_scraper import main as scrape_nexgen
from uk_scraper import main as scrape_uk
from us_scraper import main as scrape_us
from db import init_db, get_user_by_email, create_user, get_history_by_user, log_history_to_db, verify_user, get_user_settings, update_user_settings, get_all_users, update_user_permissions, make_admin, update_user_profile_photo, is_first_user
app = Flask(__name__)
app.config["SECRET_KEY"] = "dev_super_secret_key_for_session" # Required for session
CORS(app, supports_credentials=True)
init_db(app)

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

import json

# ---------------- PERSISTENCE ----------------
HISTORY_FILE = "history.json"
SETTINGS_FILE = "settings.json"

def load_json(filepath, default=[]):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except:
            pass
    return default

def save_json(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

def log_history(platform, query, count, csv_path, user_id=None):
    if user_id:
        log_history_to_db(user_id, platform, query, count, csv_path)
        return

    history = load_json(HISTORY_FILE, default=[])
    record = {
        "id": int(datetime.now().timestamp()), # Simple ID
        "scraper": platform,
        "query": query,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "items": count,
        "status": "Completed",
        "csv_path": csv_path
    }
    history.insert(0, record) # Newest first
    save_json(HISTORY_FILE, history)

# ---------------- SAVE CSV ----------------
def save_csv(filename, rows, platform=None, query=None, user_id=None):
    if not rows:
        return None, []
    # If filename is generic, make it unique to avoid overwrites if desired, 
    # but for now we keep per-scraper filenames as requested or maybe timestamped?
    # Let's keep existing filename logic but adding timestamp might be better. 
    # Since we log to history, let's make unique filenames
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name, ext = os.path.splitext(filename)
    unique_filename = f"{name}_{timestamp}{ext}"
    
    path = os.path.join(OUTPUT_DIR, unique_filename)
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
        
    # Log to history if platform is provided
    if platform:
        log_history(platform, query, len(rows), f"/output/{unique_filename}", user_id)
        
    return f"/output/{unique_filename}", rows

# ---------------- RUNNERS ----------------
# Wrapper to pass platform/query to save_csv for history logging
def run_scraper_wrapper(func, platform, query, limit):
    try:
        # Some scrapers return generators, some lists. Normalize.
        data = func(query, limit) if "gitex" not in platform and "gpt" not in platform else func(query, limit)
        if hasattr(data, '__iter__') and not isinstance(data, list):
             data = list(data)
             
        # Special handling for already wrapped functions or direct calls if needed
        # But wait, original runners match SCRAPER_MAP values. 
        # We need to refactor runners to use the new save_csv signature OR
        # Just update save_csv calls inside runners.
        pass 
    except:
        pass

# Refactoring runners to use new save_csv logic directly
# ---------------- SCRAPER MAP ----------------
# All runners need to accept (query, limit, user_id=None)
# simpler to wrap them dynamically or update them all. 
# Let's update the runners to accept **kwargs to catch user_id and pass it to save_csv


def run_linkedin_articles_scraper(query, limit, user_id=None, debug=False):
    # Pass debug and filters if needed
    data = list(scrape_linkedin_articles(query, limit, debug=debug))
    return save_csv("linkedin_articles.csv", data, "linkedin-articles", query, user_id)

def run_linkedin_jobs_scraper(query, limit, user_id=None, debug=False):
    data = list(scrape_linkedin_jobs(query, limit, save_csv=False, debug=debug))
    return save_csv("linkedin_jobs.csv", data, "linkedin-jobs", query, user_id)

# Other scrapers might not need debug yet, but we should make the signature consistent if we call them dynamically
# For now, I'll just update these two and handle the dynamic call in live_scrape carefully.

def run_twitter_scraper(query, limit, user_id=None, debug=False):
    # Twitter scraper doesn't have debug arg yet in signature, need to check file
    # But let's check twitter_scraper.py
    data = list(scrape_twitter(query, limit)) # It prints to stdout but doesn't take debug
    return save_csv("twitter.csv", data, "twitter", query, user_id)

def run_reddit_scraper(query, limit, user_id=None, debug=False):
    data = list(scrape_reddit(query, max_posts=limit, headless=(not debug)))
    return save_csv("reddit.csv", data, "reddit", query, user_id)

def run_reddit_threads_scraper(query, limit, user_id=None, debug=False):
    data = scrape_thread_reddit(query, max_threads=limit)
    return save_csv("reddit_threads.csv", data, "reddit-threads", query, user_id)

def run_speakers_scraper(query, limit, user_id=None, debug=False):
    data = list(scrape_speakers(query, limit))
    return save_csv("speakers.csv", data, "speakers", query, user_id)

def run_gitex_exhibitors(query, limit, user_id=None, debug=False):
    data = list(scrape_gitex_speakers(keyword=query, limit=limit))
    return save_csv("gitex_exhibitors.csv", data, "gitex", query, user_id)

def run_gmap_scraper(query, limit, user_id=None, debug=False):
    # Detect region from query
    region = None
    q_lower = query.lower()
    
    # United States Detection
    if any(x in q_lower for x in ["us", "usa", "unites states", "unite states", "united states", "america"]):
        region = "us"
    # UK Detection
    elif any(x in q_lower for x in ["uk", "united kingdom", "london", "england", "britain"]):
        region = "uk"
    # India Detection
    elif any(x in q_lower for x in ["india", "bharat", "delhi", "mumbai"]):
        region = "in"
    # Australia Detection
    elif any(x in q_lower for x in ["australia", "sydney", "melbourne"]):
        region = "au"
    # Canada Detection
    elif any(x in q_lower for x in ["canada", "toronto", "vancouver"]):
        region = "ca"
    # Germany
    elif any(x in q_lower for x in ["germany", "deutschland", "berlin"]):
        region = "de"
    # UAE
    elif any(x in q_lower for x in ["uae", "dubai", "emirates"]):
        region = "ae"

    data = list(scrape_gmap(query, limit, headless=(not debug), region=region))
    return save_csv("google_maps.csv", data, "google-maps", query, user_id)

def run_eauctionsindia_scraper(query, limit, user_id=None, debug=False):
    data = list(scrape_eauctionsindia(query, limit))
    return save_csv("eauctionsindia.csv", data, "eauctions", query, user_id)

def run_restaurant_scraper(query, limit, user_id=None, debug=False):
    # Scraper handles headless internally but we can't easily pass it without refactoring restaurant_scraper signature
    # calling it as is
    output_file = scrape_restaurant(query=query, limit=limit)
    rows = []
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    return save_csv("restaurants.csv", rows, "restaurants", query or "Unknown", user_id)

def run_opentable_scraper(query, limit, user_id=None, debug=False):
    if "," in query:
        parts = [x.strip() for x in query.rsplit(",", 1)]
        city = parts[0]
        country = parts[1]
    else:
        country = "us"
        city = query.strip()
    print(f"OpenTable Scrape: City='{city}', Country='{country}'")
    data = scrape_opentable(country, city, limit=limit, headless=(not debug))
    return save_csv("opentable.csv", data[:limit], "opentable", query, user_id)

def run_youtube_scraper(query, limit, user_id=None, debug=False):
    data, _ = scrape_youtube(query, max_videos=limit)
    return save_csv("youtube.csv", data, "youtube", query, user_id)

# Helper for instagram to match signature
def run_instagram_scraper(query, limit, user_id=None, debug=False):
    data = list(scrape_instagram(query, limit))
    return save_csv("instagram.csv", data, "instagram", query, user_id)

def run_instagram_articles_scraper(query, limit, user_id=None, debug=False):
    data = scrape_instagram_hashtag(query, limit)
    return save_csv("instagram_articles.csv", data, "instagram-articles", query, user_id)

# runners for new scrapers
def run_london_scraper(query, limit, user_id=None, debug=False):
    data = scrape_london()
    return save_csv("london_speakers.csv", data, "london-scraper", query, user_id)

def run_india_scraper(query, limit, user_id=None, debug=False):
    data = scrape_india()
    return save_csv("india_speakers.csv", data, "india-scraper", query, user_id)

def run_gartner_scraper(query, limit, user_id=None, debug=False):
    data = scrape_gartner()
    return save_csv("gartner_speakers.csv", data, "gartner", query, user_id)

def run_bharat_2025_scraper(query, limit, user_id=None, debug=False):
    data = scrape_bharat_2025()
    return save_csv("bharat_2025_speakers.csv", data, "bharat-2025", query, user_id)

def run_bharat_2023_scraper(query, limit, user_id=None, debug=False):
    # Pointing to fintech scraper since 2023 is missing
    data = scrape_bharat_fintech()
    return save_csv("bharat_2023_speakers.csv", data, "bharat-2023", query, user_id)

def run_bharat_fintech_scraper(query, limit, user_id=None, debug=False):
    data = scrape_bharat_fintech()
    return save_csv("bharat_fintech_speakers.csv", data, "bharat-fintech", query, user_id)

def run_fof_scraper(query, limit, user_id=None, debug=False):
    data = scrape_fof()
    return save_csv("fof_speakers.csv", data, "fof", query, user_id)

def run_isb_scraper(query, limit, user_id=None, debug=False):
    data = scrape_isb()
    return save_csv("indian_speaker_bureau_speakers.csv", data, "isb", query, user_id)

def run_lsb_scraper(query, limit, user_id=None, debug=False):
    data = scrape_lsb()
    return save_csv("london_speaker_bureau_speakers.csv", data, "lsb", query, user_id)

def run_nexgen_scraper(query, limit, user_id=None, debug=False):
    data = scrape_nexgen()
    return save_csv("nexgen_speakers.csv", data, "nexgen", query, user_id)

def run_leading_authorities_scraper(query, limit, user_id=None, debug=False):
    data = scrape_leading_authorities(query=query, limit=limit)
    return save_csv("leading_authorities_speakers.csv", data, "leading-authorities", query, user_id)

def run_uk_scraper(query, limit, user_id=None, debug=False):
    data = scrape_uk()
    return save_csv("uk_speakers.csv", data, "uk-scraper", query, user_id)

def run_us_scraper(query, limit, user_id=None, debug=False):
    data = scrape_us(query=query, limit=limit)
    return save_csv("us_speakers.csv", data, "us-scraper", query, user_id)

def run_europe_scraper(query, limit, user_id=None, debug=False):
    data = scrape_europe(query=query, limit=limit)
    return save_csv("europe_speakers.csv", data, "europe-scraper", query, user_id)


SCRAPER_MAP = {
    "instagram": run_instagram_scraper,
    "instagram_scraper": run_instagram_scraper,
    "instagram_articles": run_instagram_articles_scraper,
    "linkedin_articles": run_linkedin_articles_scraper,
    "linkedin_jobs": run_linkedin_jobs_scraper,
    "linkedin_jobs_scraper": run_linkedin_jobs_scraper,
    "linkedinjob_scraper": run_linkedin_jobs_scraper,
    "twitter": run_twitter_scraper,
    "reddit": run_reddit_scraper,
    "reddit_threads": run_reddit_threads_scraper,
    "speakers": run_speakers_scraper,
    "gitex_exhibitors": run_gitex_exhibitors,
    "gitex": run_gitex_exhibitors,
    "gmap_scraper": run_gmap_scraper,
    "google_maps": run_gmap_scraper,
    "eauctionsindia": run_eauctionsindia_scraper,
    "eauctions": run_eauctionsindia_scraper,
    "restaurant_scraper": run_restaurant_scraper,
    "restaurants": run_restaurant_scraper,
    "opentable_restaurant": run_opentable_scraper,
    "opentable": run_opentable_scraper,
    "youtube": run_youtube_scraper,
    "youtube_scraper": run_youtube_scraper,
    "london-scraper": run_london_scraper,
    "india-scraper": run_india_scraper,
    "gartner-scraper": run_gartner_scraper,
    "bharat-2025": run_bharat_2025_scraper,
    "bharat-2023": run_bharat_2023_scraper,
    "bharat-fintech": run_bharat_fintech_scraper,
    "fof-scraper": run_fof_scraper,
    "isb-scraper": run_isb_scraper,
    "lsb-scraper": run_lsb_scraper,
    "nexgen-scraper": run_nexgen_scraper,
    "leading-authorities": run_leading_authorities_scraper,
    "uk-scraper": run_uk_scraper,
    "us-scraper": run_us_scraper,
    "europe-scraper": run_europe_scraper
}

# ---------------- ROUTES ----------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "ok",
        "message": "Scraper API running",
        "time": str(datetime.now())
    })
@app.route("/api/admin/create_user", methods=["POST"])
def admin_create_user_route():
    # Verify admin status manually since @login_required might rely on session
    # and we act as API. But let's check session 'user'
    print(f"DEBUG: Session keys: {list(session.keys())}")
    email = session.get("user")
    print(f"DEBUG: Session user email: {email}")
    
    if not email:
        print("DEBUG: No email in session, returning 401")
        return jsonify({"error": "Unauthorized"}), 401
        
    current_user = get_user_by_email(email)
    if not current_user:
         print(f"DEBUG: User not found for email {email}")
         return jsonify({"error": "Unauthorized"}), 403
         
    if current_user.get("role") != "admin":
        print(f"DEBUG: User {email} is not admin. Role: {current_user.get('role')}")
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    if not data or not data.get("email") or not data.get("password") or not data.get("name"):
        return jsonify({"error": "Missing fields"}), 400

    if get_user_by_email(data["email"]):
        return jsonify({"error": "Email already registered"}), 400

    try:
        # Default to empty modules if not provided, or provided list
        allowed_modules = data.get("allowed_modules", [])
        create_user(data["name"], data["email"], data["password"], role="user", allowed_modules=allowed_modules)
        return jsonify({"message": "User created successfully", "status": "success"}), 201
    except Exception as e:
        print(f"Error creating user: {e}")
        return jsonify({"error": "Failed to create user"}), 500

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    name = data.get("name")
    password = data.get("password") # Expect password
    
    if not email:
        return jsonify({"error": "Email required"}), 400
    if not password:
         return jsonify({"error": "Password required"}), 400
        
    # Check if user exists
    existing_user = get_user_by_email(email)
    
    if existing_user:
        # Verify credentials
        user = verify_user(email, password)
        if user:
            user_id = str(user["_id"])
            session["user"] = email # Set session for auth
            history = get_history_by_user(user_id)
            return jsonify({
                "status": "exists",
                "userId": user_id,
                "name": user.get("name"),
                "email": user.get("email"),
                "role": user.get("role", "user"),
                "allowed_modules": user.get("allowed_modules", []),
                "profile_photo": user.get("profile_photo"),
                "history": history
            })
        else:
            return jsonify({"error": "Invalid credentials"}), 401
    else:
        # New user - create and return user ID with empty history
        # Name is required for registration
        if not name:
            name = email.split("@")[0] # Fallback name
        
        # Check if this is the first user - auto-assign admin role
        first_user = is_first_user()
        role = "admin" if first_user else "user"
        
        # All modules for first user (admin), default modules for others
        all_modules = ["linkedin-articles", "linkedin-jobs", "twitter", "reddit", "instagram", "youtube", "google-maps", "speakers", "gitex", "eauctions", "restaurants", "opentable", "reddit-threads", "instagram-articles"]
        
        user_id = create_user(name, email, password, role=role)
        session["user"] = email # Set session for auth
        
        return jsonify({
            "status": "created",
            "userId": user_id,
            "name": name,
            "email": email,
            "role": role,
            "allowed_modules": all_modules,
            "history": []
        })

@app.route("/output/<path:filename>")
def download_file(filename):
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)

@app.route("/uploads/<path:filename>")
def serve_upload(filename):
    return send_from_directory("uploads", filename)

@app.route("/api/upload_profile_photo", methods=["POST"])
def upload_profile_photo():
    if "photo" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["photo"]
    user_id = request.form.get("userId")
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    if file and user_id:
        os.makedirs("uploads", exist_ok=True)
        # Use userId to name the file to avoid collisions/overwrite
        ext = os.path.splitext(file.filename)[1]
        filename = f"profile_{user_id}{ext}"
        filepath = os.path.join("uploads", filename)
        file.save(filepath)
        
        # URL to access the file
        photo_url = f"/uploads/{filename}"
        
        # Update DB
        if update_user_profile_photo(user_id, photo_url):
            return jsonify({"status": "success", "photoUrl": photo_url})
        else:
            return jsonify({"error": "Database update failed"}), 500
    return jsonify({"error": "Upload failed"}), 500

@app.route("/api/live_scrape", methods=["GET"])
@app.route("/api/live_scrape", methods=["GET"])
def live_scrape():
    platform = request.args.get("platform")
    query = request.args.get("query")
    limit = request.args.get("limit", 5)
    user_id = request.args.get("userId") # Get user ID
    debug_param = request.args.get("debug", "false").lower()
    debug = debug_param == "true"

    if not platform:
        return jsonify({"success": False, "error": "platform required"}), 400

    try:
        limit = int(limit)
    except:
        return jsonify({"success": False, "error": "limit must be integer"}), 400

    scraper = SCRAPER_MAP.get(platform)
    if not scraper:
        # Try finding partial match or just return error
        return jsonify({
            "success": False,
            "error": f"Invalid platform: {platform}",
            "available_platforms": list(SCRAPER_MAP.keys())
        }), 400

    try:
        # Runners now handle history logging internally
        # All runners should accept debug kwarg now
        csv_path, rows = scraper(query, limit, user_id=user_id, debug=debug)
        return jsonify({
            "success": True,
            "platform": platform,
            "query": query,
            "scraped": len(rows),
            "data": rows,
            "csv_file": csv_path,
            "time": str(datetime.now())
        })
    except Exception as e:
        traceback.print_exc()
        # Return 200 so the frontend definitely parses the JSON error message
        return jsonify({"success": False, "error": str(e)}), 200

@app.route("/api/history", methods=["GET"])
def get_history():
    user_id = request.args.get("userId")
    if user_id:
        # Return MongoDB history for this user
        return jsonify(get_history_by_user(user_id))
    
    # Strict isolation: No user ID -> No history
    return jsonify([])

@app.route("/api/history", methods=["DELETE"])
def clear_history():
    # TODO: Implement delete in DB if needed, or just leave as stub
    # User didn't explicitly ask for delete, but good to have
    # save_json(HISTORY_FILE, []) 
    return jsonify({"success": True, "message": "History cleared (not implemented for individual DB items yet)"})

@app.route("/api/settings", methods=["GET"])
def get_settings():
    settings = {}
    
    # 1. Load system-level settings (driver path)
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                settings.update(json.load(f))
        except:
            pass

    user_id = request.args.get("userId")
    if user_id:
        # 2. Merge with user-specific settings
        user_settings = get_user_settings(user_id)
        settings.update(user_settings)
        return jsonify(settings)
    
    # Return defaults if no user (but still include system settings)
    defaults = {
        "username": "Guest",
        "email": "",
        "theme": "dark",
        "notifications": True
    }
    defaults.update(settings)
    return jsonify(defaults)

@app.route("/api/settings", methods=["POST"])
def update_settings():
    data = request.json
    user_id = data.get("userId")
    if user_id:
        # Update specific settings keys
        # First get existing to merge? Or just update what's passed
        # For MongoDB simplification, we might want to just set the whole object or patch it.
        # Let's patch.
        current = get_user_settings(user_id)
        current.update(data)
        # Remove userId from stored settings if it crept in
        if "userId" in current: del current["userId"]
        
        update_user_settings(user_id, current)
        return jsonify({"success": True, "settings": current})
        
    return jsonify({"success": False, "error": "userId required"}), 400

@app.route("/api/install_driver", methods=["POST"])
def install_driver_api():
    try:
        from driver_utils import install_configured_driver
        version = request.json.get("version", "latest")
        path = install_configured_driver(version)
        
        # Reload settings to get the updated path
        updated_settings = {}
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    updated_settings = json.load(f)
            except:
                pass
                
        return jsonify({
            "success": True, 
            "message": f"Driver installed successfully",
            "path": path,
            "settings": updated_settings
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/users", methods=["GET"])
def get_users_api():
    # In a real app, verify admin session/token here
    # For now, we trust the frontend (or pass a secret header if we wanted more security)
    users = get_all_users()
    return jsonify(users)

@app.route("/api/users/permissions", methods=["POST"])
def update_permissions_api():
    data = request.json
    user_id = data.get("userId")
    allowed = data.get("allowed_modules")
    
    if update_user_permissions(user_id, allowed):
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Update failed"}), 400

# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=61631, debug=True)
