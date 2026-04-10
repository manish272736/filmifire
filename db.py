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