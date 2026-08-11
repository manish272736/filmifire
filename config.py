import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-in-prod")
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/filmifire")
    
    # TMDB Configuration
    TMDB_API_KEY = os.environ.get("TMDB_API_KEY", "51282d539e9667a3adb31d4158549000")

    # Cloudinary
    CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY = os.environ.get("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET")

    # FCM Push Notifications (v1 API)
    FCM_SERVICE_ACCOUNT_PATH = os.environ.get("FCM_SERVICE_ACCOUNT_PATH", "fcm-service-account.json")
    FCM_PROJECT_ID = os.environ.get("FCM_PROJECT_ID", "filmifire-fa205")
    FCM_SERVICE_ACCOUNT_JSON = os.environ.get("FCM_SERVICE_ACCOUNT_JSON", "")

    CATEGORIES = [
        {"slug": "news",      "label": "News"},
        {"slug": "photos",    "label": "Photos"},
        {"slug": "bollywood", "label": "Bollywood"},
        {"slug": "kollywood", "label": "Kollywood"},
        {"slug": "tollywood", "label": "Tollywood"},
        {"slug": "mollywood", "label": "Mollywood"},
        {"slug": "sandalwood","label": "Sandalwood"},
        {"slug": "box-office","label": "Box Office"},
        {"slug": "records",   "label": "Records"},
        {"slug": "reviews",   "label": "Reviews"},
    ]