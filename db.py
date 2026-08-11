from pymongo import MongoClient, TEXT
from pymongo.errors import OperationFailure
from flask import current_app
import certifi
import warnings

# Suppress the fork-safety warning since Render uses only 1 worker
warnings.filterwarnings("ignore", message=".*MongoClient opened before fork.*")

_client = None

def get_db():
    global _client
    if _client is None:
        _client = MongoClient(
            current_app.config["MONGO_URI"],
            tlsCAFile=certifi.where(),
            tls=True
        )
    return _client["filmifire"]

def init_db(app):
    with app.app_context():
        db = get_db()
        try:
            db.articles.create_index(
                [("title", TEXT), ("tags", TEXT), ("excerpt", TEXT)],
                name="article_search"
            )
        except OperationFailure:
            pass
        db.articles.create_index("slug", unique=True)
        db.articles.create_index("category")
        db.articles.create_index("status")
        db.articles.create_index("published_at")

        # ── Live Box Office Tracker Helpers ──────────────────────────────────────────

def get_active_trackers():
    """Returns all movies currently active in tracking."""
    db = get_db()
    return list(db.tracked_movies.find({"status": "active"}).sort("last_updated", -1))

def get_tracker_by_slug(slug):
    """Returns a specific movie tracker document by its slug."""
    db = get_db()
    return db.tracked_movies.find_one({"slug": slug})

def create_or_update_tracked_movie(movie_data):
    """Upserts a tracked movie document into MongoDB."""
    db = get_db()
    slug = movie_data.get("slug")
    db.tracked_movies.update_one(
        {"slug": slug},
        {"$set": movie_data},
        upsert=True
    )