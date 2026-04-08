from pymongo import MongoClient, TEXT
from pymongo.errors import OperationFailure
from flask import current_app, g
import certifi

def get_db():
    if 'db_client' not in g:
        g.db_client = MongoClient(
            current_app.config["MONGO_URI"],
            tlsCAFile=certifi.where(),
            tls=True,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
        )
    return g.db_client["filmifire"]

def init_db(app):
    with app.app_context():
        client = MongoClient(
            app.config["MONGO_URI"],
            tlsCAFile=certifi.where(),
            tls=True,
            serverSelectionTimeoutMS=5000,
        )
        db = client["filmifire"]
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
        client.close()