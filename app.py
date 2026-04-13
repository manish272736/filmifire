from flask import Flask, redirect, request, send_from_directory
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

    # ── Fix 404 — redirect /home/ → / ────────────────────────────────────────
    @app.route('/home/')
    @app.route('/home')
    def redirect_home():
        return redirect('/', 301)

    # ── robots.txt ────────────────────────────────────────────────────────────
    @app.route('/robots.txt')
    def robots():
        return send_from_directory(app.static_folder, 'robots.txt')


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

    init_db(app)
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)