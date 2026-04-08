from flask import Flask, send_from_directory, redirect, request
from extensions import login_manager
from config import Config
from db import init_db, get_db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50MB

    login_manager.init_app(app)

    # ── Redirect onrender.com → filmifire.com ─────────────────────────────────
    @app.before_request
    def redirect_to_custom_domain():
        if 'onrender.com' in request.host:
            url = 'https://filmifire.com' + request.full_path.rstrip('?')
            return redirect(url, 301)

    from blueprints.main import main_bp
    from blueprints.admin import admin_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")

    @app.context_processor
    def inject_globals():
        try:
            db = get_db()
            ticker_headlines = list(db.articles.find(
                {"status": "published", "ticker": True, "archived": {"$ne": True}},
                {"title": 1, "slug": 1},
                sort=[("published_at", -1)],
                limit=6
            ))
        except Exception:
            ticker_headlines = []
        return {
            "categories": app.config["CATEGORIES"],
            "ticker_headlines": ticker_headlines
        }

    # ── robots.txt ────────────────────────────────────────────────────────────
    @app.route("/robots.txt")
    def robots():
        return send_from_directory(app.static_folder, "robots.txt")

    # ── Close MongoDB connection after each request ───────────────────────────
    @app.teardown_appcontext
    def close_db(error):
        from flask import g
        client = g.pop('db_client', None)
        if client is not None:
            client.close()

    init_db(app)
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)