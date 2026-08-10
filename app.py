from flask import Flask, redirect, request, send_from_directory, abort
import os
from extensions import login_manager
from config import Config
from db import init_db, get_db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50MB
    login_manager.init_app(app)

    # ── Lightweight Health Check Endpoint ─────────────────────────────────
    @app.route('/healthz')
    def health_check():
        return "OK", 200

    # ── Redirect onrender.com → filmifire.com (Excludes /healthz) ───────────
    @app.before_request
    def redirect_to_custom_domain():
        # Do not redirect health checks so Render's internal checks always pass directly
        if request.path == '/healthz':
            return None
        if request and 'onrender.com' in request.host:
            url = 'https://filmifire.com' + request.full_path.rstrip('?')
            return redirect(url, 301)

    # ── /home/ → 410 Gone (removes redirect error from Search Console) ────
    @app.route('/home/')
    @app.route('/home')
    def home_gone():
        abort(410)

    # ── Serve Firebase SW from ROOT so it can control all pages ──────────
    @app.route('/firebase-messaging-sw.js')
    def firebase_sw():
        return send_from_directory(
            os.path.join(app.root_path, 'static'),
            'firebase-messaging-sw.js',
            mimetype='application/javascript'
        )

    # ── robots.txt ────────────────────────────────────────────────────────
    @app.route('/robots.txt')
    def robots():
        return send_from_directory(app.static_folder, 'robots.txt')

    # ── ads.txt ───────────────────────────────────────────────────────────
    @app.route('/ads.txt')
    def ads_txt():
        return send_from_directory(app.static_folder, 'ads.txt')

    # ── IndexNow key file — served from root for Bing verification ───────
    @app.route('/<key_file>')
    def indexnow_key(key_file):
        if key_file.endswith('.txt') and key_file != 'robots.txt':
            try:
                return send_from_directory(app.static_folder, key_file,
                                           mimetype='text/plain')
            except Exception:
                pass
        abort(404)

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