import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-in-prod")
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/filmifire")
    CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY = os.environ.get("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET")

    # FCM Push Notifications (v1 API)
    # Uses the JSON file directly — more reliable than env var for multi-line JSON
    FCM_SERVICE_ACCOUNT_PATH = os.environ.get("FCM_SERVICE_ACCOUNT_PATH", "fcm-service-account.json")
    FCM_PROJECT_ID = os.environ.get("FCM_PROJECT_ID", "filmifire-fa205")
    # FCM_SERVICE_ACCOUNT_JSON kept for fallback but file path is primary
    FCM_SERVICE_ACCOUNT_JSON = os.environ.get("FCM_SERVICE_ACCOUNT_JSON", "")

    CATEGORIES = [
        {"slug": "news",       "label": "News"},
        {"slug": "photos",     "label": "Photos"},
        {"slug": "bollywood",  "label": "Bollywood"},
        {"slug": "kollywood",  "label": "Kollywood"},
        {"slug": "tollywood",  "label": "Tollywood"},
        {"slug": "mollywood",  "label": "Mollywood"},
        {"slug": "sandalwood", "label": "Sandalwood"},
        {"slug": "box-office", "label": "Box Office"},
        {"slug": "records",    "label": "Records"},
    ]