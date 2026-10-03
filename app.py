import os
import firebase_admin
from firebase_admin import credentials
from flask import Flask, redirect, request, send_from_directory, abort
from apscheduler.schedulers.background import BackgroundScheduler

from extensions import login_manager
from config import Config
from db import init_db, get_db
from tracker_service import sync_active_trackers


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50MB
    login_manager.init_app(app)

    # ── Initialize Firebase Admin SDK ───────────────────────────────────────
    if not firebase_admin._apps:
        try:
            cred_path = os.path.join(app.root_path, "fcm-service-account.json")
            if os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                print("--- Firebase Initialized Successfully ---")
            else:
                print(f"!!! Firebase JSON file not found at path: {cred_path}")
        except Exception as e:
            print(f"!!! Firebase Initialization Failed: {e}")

    # ── Lightweight Health Check Endpoint ─────────────────────────────────
    @app.route('/healthz')
    def health_check():
        return "OK", 200

    # ── Redirect onrender.com → filmifire.com (Excludes /healthz) ───────────
    @app.before_request
    def redirect_to_custom_domain():
        if request.path == '/healthz':
            return None
        if request and 'onrender.com' in request.host:
            url = 'https://filmifire.com' + request.full_path.rstrip('?')
            return redirect(url, 301)

    # ── /home/ → 410 Gone ──────────────────────────────────────────────────
    @app.route('/home/')
    @app.route('/home')
    def home_gone():
        abort(410)

    # ── Serve Firebase SW from ROOT ────────────────────────────────────────
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

   # ── IndexNow key file ──────────────────────────────────────────────────
    @app.route('/verify/')
    def indexnow_key(key_file):
        # Only allow verification text files and prevent directory traversal
        if key_file and key_file.endswith('.txt') and key_file != 'robots.txt' and '/' not in key_file:
            try:
                return send_from_directory(
                    app.static_folder, 
                    key_file,
                    mimetype='text/plain'
                )
            except Exception:
                pass
        abort(404)
        
    # ── Manual Sync Route for Debugging ───────────────────────────────────
    @app.route('/admin/sync', methods=['POST'])
    def manual_sync():
        try:
            print("--- Manual Sync Started ---")
            sync_active_trackers(app)
            print("--- Manual Sync Finished ---")
            return {"status": "success", "message": "Manual sync completed."}, 200
        except Exception as e:
            print(f"!!! Manual Sync Failed: {e}")
            return {"status": "error", "message": str(e)}, 500

    # ── Register Blueprints ───────────────────────────────────────────────
    from blueprints.main import main_bp
    from blueprints.admin import admin_bp
    from blueprints.tracker import tracker_bp  # <-- Tracker blueprint imported

    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(tracker_bp, url_prefix="/box-office")  # <-- Registered with /box-office prefix

    # ── Context Processor ─────────────────────────────────────────────────
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
            "categories": app.config.get("CATEGORIES", []),
            "ticker_headlines": ticker_headlines
        }

    init_db(app)

    # ── Initialize 4x Daily Box Office Background Scheduler ───────────
    if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        scheduler = BackgroundScheduler(timezone="Asia/Kolkata")
        
        # Runs at 09:30 AM, 02:30 PM, 07:00 PM, and 11:00 PM IST
        scheduler.add_job(
            func=lambda: sync_active_trackers(app),
            trigger='cron',
            hour='9,14,19,23',
            minute='30',
            id='box_office_daily_sync',
            replace_existing=True
        )
        scheduler.start()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)