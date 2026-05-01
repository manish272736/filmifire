from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, UserMixin, current_user
from db import get_db
from extensions import login_manager
from bson import ObjectId
import bcrypt
import re
import datetime
import cloudinary
import cloudinary.uploader
from flask import current_app
from .indexnow import ping_indexnow, ping_indexnow_bulk

admin_bp = Blueprint("admin", __name__)

# ── User model (single admin) ─────────────────────────────────────────────────
class AdminUser(UserMixin):
    def __init__(self, user_doc):
        self.id = str(user_doc["_id"])
        self.email = user_doc["email"]

@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    doc = db.admins.find_one({"_id": ObjectId(user_id)})
    return AdminUser(doc) if doc else None

# ── Helpers ───────────────────────────────────────────────────────────────────
def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    text = re.sub(r"^-+|-+$", "", text)
    return text

def unique_slug(db, base_slug, exclude_id=None):
    slug = base_slug
    counter = 1
    while True:
        query = {"slug": slug}
        if exclude_id:
            query["_id"] = {"$ne": ObjectId(exclude_id)}
        if not db.articles.find_one(query):
            return slug
        slug = f"{base_slug}-{counter}"
        counter += 1

def parse_rating(val):
    """Parse rating from form — returns float 0.5-5 in 0.5 steps, or None"""
    try:
        r = float(val)
        r = round(r * 2) / 2
        return r if 0.5 <= r <= 5 else None
    except (TypeError, ValueError):
        return None

# ── IndexNow — ping Bing/Yahoo when articles are published ───────────────────

@admin_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("admin.login"))

# ── Dashboard ─────────────────────────────────────────────────────────────────
@admin_bp.route("/")
@login_required
def dashboard():
    db = get_db()
    articles = list(db.articles.find(
        {},
        sort=[("published_at", -1)],
        limit=50
    ))
    stats = {
        "total": db.articles.count_documents({}),
        "published": db.articles.count_documents({"status": "published"}),
        "drafts": db.articles.count_documents({"status": "draft"}),
        "views": sum(a.get("views", 0) for a in db.articles.find({}, {"views": 1}))
    }
    return render_template("admin/dashboard.html", articles=articles, stats=stats)

# ── New article ───────────────────────────────────────────────────────────────
@admin_bp.route("/new", methods=["GET", "POST"])
@login_required
def new_article():
    from config import Config
    if request.method == "POST":
        db = get_db()
        title = request.form.get("title", "").strip()
        body_html = request.form.get("body_html", "")
        excerpt = request.form.get("excerpt", "").strip()
        category = request.form.get("category", "")
        tags_raw = request.form.get("tags", "")
        tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
        status = request.form.get("status", "draft")
        author = request.form.get("author", "").strip()
        featured = "featured" in request.form
        pinned = "pinned" in request.form
        ticker = "ticker" in request.form
        carousel = "carousel" in request.form
        cover_img = request.form.get("cover_img_url", "").strip()
        rating = parse_rating(request.form.get("rating", ""))
        movie_name = request.form.get("movie_name", "").strip()

        if "cover_img" in request.files:
            f = request.files["cover_img"]
            if f and f.filename:
                cloudinary.config(
                    cloud_name=current_app.config["CLOUDINARY_CLOUD_NAME"],
                    api_key=current_app.config["CLOUDINARY_API_KEY"],
                    api_secret=current_app.config["CLOUDINARY_API_SECRET"]
                )
                public_id_base = f'filmifire/{__import__("uuid").uuid4().hex[:12]}'
                result = cloudinary.uploader.upload(
                    f,
                    public_id=public_id_base,
                    overwrite=True,
                    quality="auto",
                    fetch_format="auto"
                )
                raw_id = result.get("public_id", "")
                cloud = current_app.config["CLOUDINARY_CLOUD_NAME"]
                cover_img = f"https://res.cloudinary.com/{cloud}/image/upload/w_1200,h_675,c_pad,b_black,q_auto/{raw_id}.jpg"

        base_slug = slugify(title)
        slug = unique_slug(db, base_slug)

        doc = {
            "title": title,
            "slug": slug,
            "body_html": body_html,
            "excerpt": excerpt,
            "cover_img": cover_img,
            "category": category,
            "tags": tags,
            "status": status,
            "author": author,
            "featured": featured,
            "pinned": pinned,
            "ticker": ticker,
            "carousel": carousel,
            "rating": rating,
            "movie_name": movie_name if movie_name else None,
            "views": 0,
            "created_at": datetime.datetime.utcnow(),
            "published_at": datetime.datetime.utcnow() if status == "published" else None,
        }
        db.articles.insert_one(doc)

        if status == "published":
            ping_indexnow(slug)

        flash("Article saved!", "success")
        return redirect(url_for("admin.dashboard"))
    return render_template("admin/editor.html",
        article=None,
        categories=Config.CATEGORIES
    )

# ── Edit article ──────────────────────────────────────────────────────────────
@admin_bp.route("/edit/<article_id>", methods=["GET", "POST"])
@login_required
def edit_article(article_id):
    from config import Config
    db = get_db()
    art = db.articles.find_one({"_id": ObjectId(article_id)})
    if not art:
        flash("Article not found.", "error")
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        body_html = request.form.get("body_html", "")
        excerpt = request.form.get("excerpt", "").strip()
        category = request.form.get("category", "")
        tags_raw = request.form.get("tags", "")
        tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
        status = request.form.get("status", "draft")
        author = request.form.get("author", "").strip()
        featured = "featured" in request.form
        pinned = "pinned" in request.form
        ticker = "ticker" in request.form
        carousel = "carousel" in request.form
        cover_img = request.form.get("cover_img_url", art.get("cover_img", ""))
        rating = parse_rating(request.form.get("rating", ""))
        movie_name = request.form.get("movie_name", "").strip()

        if "cover_img" in request.files:
            f = request.files["cover_img"]
            if f and f.filename:
                cloudinary.config(
                    cloud_name=current_app.config["CLOUDINARY_CLOUD_NAME"],
                    api_key=current_app.config["CLOUDINARY_API_KEY"],
                    api_secret=current_app.config["CLOUDINARY_API_SECRET"]
                )
                public_id_base = f'filmifire/{__import__("uuid").uuid4().hex[:12]}'
                result = cloudinary.uploader.upload(
                    f,
                    public_id=public_id_base,
                    overwrite=True,
                    quality="auto",
                    fetch_format="auto"
                )
                raw_id = result.get("public_id", "")
                cloud = current_app.config["CLOUDINARY_CLOUD_NAME"]
                cover_img = f"https://res.cloudinary.com/{cloud}/image/upload/w_1200,h_675,c_pad,b_black,q_auto/{raw_id}.jpg"

        update = {
            "title": title,
            "body_html": body_html,
            "excerpt": excerpt,
            "cover_img": cover_img,
            "category": category,
            "tags": tags,
            "status": status,
            "author": author,
            "featured": featured,
            "pinned": pinned,
            "ticker": ticker,
            "carousel": carousel,
            "rating": rating,
            "movie_name": movie_name if movie_name else None,
            "updated_at": datetime.datetime.utcnow(),
        }
        if status == "published" and not art.get("published_at"):
            update["published_at"] = datetime.datetime.utcnow()

        db.articles.update_one({"_id": ObjectId(article_id)}, {"$set": update})

        if status == "published":
            ping_indexnow(art.get("slug", ""))

        flash("Article updated!", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("admin/editor.html",
        article=art,
        categories=Config.CATEGORIES
    )

# ── Delete article ────────────────────────────────────────────────────────────
@admin_bp.route("/delete/<article_id>", methods=["POST"])
@login_required
def delete_article(article_id):
    db = get_db()
    db.articles.delete_one({"_id": ObjectId(article_id)})
    flash("Article deleted.", "info")
    return redirect(url_for("admin.dashboard"))

# ── Archive / unarchive article ───────────────────────────────────────────────
@admin_bp.route("/archive/<article_id>", methods=["POST"])
@login_required
def archive_article(article_id):
    db = get_db()
    art = db.articles.find_one({"_id": ObjectId(article_id)})
    if not art:
        flash("Article not found.", "error")
        return redirect(url_for("admin.dashboard"))
    new_status = not art.get("archived", False)
    db.articles.update_one(
        {"_id": ObjectId(article_id)},
        {"$set": {"archived": new_status}}
    )
    flash("Article archived." if new_status else "Article restored to active.", "info")
    return redirect(url_for("admin.dashboard"))

# ── Bulk IndexNow ping — visit once to submit all existing articles ───────────
@admin_bp.route("/setup", methods=["GET", "POST"])
def setup():
    db = get_db()
    if db.admins.count_documents({}) > 0:
        return "Admin already exists.", 403
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").encode()
        pw_hash = bcrypt.hashpw(password, bcrypt.gensalt())
        db.admins.insert_one({"email": email, "pw_hash": pw_hash})
        return redirect(url_for("admin.login"))
    return """
    <form method="POST" style="max-width:360px;margin:60px auto;font-family:sans-serif">
      <h2>Create Admin</h2>
      <input name="email" type="email" placeholder="Email" required
             style="display:block;width:100%;padding:8px;margin:8px 0">
      <input name="password" type="password" placeholder="Password" required
             style="display:block;width:100%;padding:8px;margin:8px 0">
      <button type="submit" style="padding:8px 20px">Create</button>
    </form>"""


# ── IndexNow bulk ping (run once after setup) ─────────────────────────────────
@admin_bp.route("/ping-indexnow-all")
@login_required
def ping_indexnow_all():
    """Ping Bing IndexNow for ALL published articles — run once after setup"""
    db = get_db()
    articles = list(db.articles.find(
        {"status": "published", "archived": {"$ne": True}},
        {"slug": 1}
    ))
    slugs = [a["slug"] for a in articles if a.get("slug")]
    result = ping_indexnow_bulk(slugs)
    return jsonify({
        "total_articles": len(slugs),
        "sent": result.get("sent", 0),
        "ok": result.get("ok", False),
        "error": result.get("error", None)
    })

# ── Push Notifications ────────────────────────────────────────────────────────
@admin_bp.route("/save-push-token", methods=["POST"])
def save_push_token():
    data = request.get_json()
    token = (data.get("token", "") or "").strip() if data else ""
    if not token:
        return jsonify({"error": "No token"}), 400
    db = get_db()
    db.push_tokens.update_one(
        {"token": token},
        {"$set": {"token": token, "updated_at": datetime.datetime.utcnow()}},
        upsert=True
    )
    return jsonify({"ok": True})

@admin_bp.route("/send-notification", methods=["POST"])
@login_required
def send_notification():
    try:
        return _do_send_notification()
    except Exception as e:
        import traceback
        return jsonify({"error": f"Unexpected error: {str(e)}", "trace": traceback.format_exc()[-500:]}), 500

def _do_send_notification():
    import requests as http_requests
    import google.auth.transport.requests
    import google.oauth2.service_account
    import json
    import os

    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body sent"}), 400
    title = (data.get("title") or "FilmiFire").strip()
    body  = (data.get("body") or "").strip()
    url   = (data.get("url") or "https://filmifire.com").strip()

    if not body:
        return jsonify({"error": "Message body is required"}), 400

    project_id = current_app.config.get("FCM_PROJECT_ID", "").strip()
    if not project_id:
        return jsonify({"error": "FCM_PROJECT_ID not set"}), 500

    sa_json_str = current_app.config.get("FCM_SERVICE_ACCOUNT_JSON", "").strip()
    sa_path = current_app.config.get("FCM_SERVICE_ACCOUNT_PATH", "").strip()

    try:
        if sa_path and os.path.exists(sa_path):
            credentials = google.oauth2.service_account.Credentials.from_service_account_file(
                sa_path,
                scopes=["https://www.googleapis.com/auth/firebase.messaging"]
            )
        elif sa_json_str:
            sa_info = json.loads(sa_json_str.strip())
            credentials = google.oauth2.service_account.Credentials.from_service_account_info(
                sa_info,
                scopes=["https://www.googleapis.com/auth/firebase.messaging"]
            )
        else:
            return jsonify({"error": "No service account found"}), 500

        auth_req = google.auth.transport.requests.Request()
        credentials.refresh(auth_req)
        access_token = credentials.token
    except json.JSONDecodeError as e:
        return jsonify({"error": f"Invalid JSON: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Auth failed: {str(e)}"}), 500

    db = get_db()
    tokens = [t["token"] for t in db.push_tokens.find({}, {"token": 1})]
    if not tokens:
        return jsonify({"sent": 0, "total": 0, "cleaned": 0})

    fcm_url = f"https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

    sent = 0
    failed_tokens = []
    for token in tokens:
        payload = {
            "message": {
                "token": token,
                "notification": {"title": title, "body": body},
                "webpush": {
                    "notification": {"title": title, "body": body,
                                     "icon": "https://filmifire.com/static/favicon-32x32.png",
                                     "requireInteraction": False},
                    "fcm_options": {"link": url}
                },
                "data": {"url": url}
            }
        }
        try:
            resp = http_requests.post(fcm_url, json=payload, headers=headers, timeout=8)
            if resp.status_code == 200:
                sent += 1
            elif resp.status_code in (400, 404):
                err = resp.json().get("error", {}).get("details", [{}])
                if err and err[0].get("errorCode", "") in ("UNREGISTERED", "INVALID_ARGUMENT"):
                    failed_tokens.append(token)
        except Exception:
            pass

    if failed_tokens:
        db.push_tokens.delete_many({"token": {"$in": failed_tokens}})

    return jsonify({"sent": sent, "total": len(tokens), "cleaned": len(failed_tokens)})

@admin_bp.route("/push-subscriber-count")
@login_required
def push_subscriber_count():
    db = get_db()
    return jsonify({"count": db.push_tokens.count_documents({})})

@admin_bp.route("/test-fcm-config")
@login_required
def test_fcm_config():
    import os, json
    result = {}
    sa_path = current_app.config.get("FCM_SERVICE_ACCOUNT_PATH", "")
    sa_json = current_app.config.get("FCM_SERVICE_ACCOUNT_JSON", "")
    project_id = current_app.config.get("FCM_PROJECT_ID", "")
    result["project_id"] = project_id or "NOT SET"
    result["sa_path"] = sa_path
    result["sa_path_exists"] = os.path.exists(sa_path) if sa_path else False
    result["sa_json_length"] = len(sa_json)
    result["sa_json_starts_with"] = sa_json[:30] if sa_json else "EMPTY"
    if sa_path and os.path.exists(sa_path):
        try:
            with open(sa_path) as f:
                data = json.load(f)
            result["file_parse"] = "OK — project: " + data.get("project_id", "?")
        except Exception as e:
            result["file_parse"] = f"FAILED: {e}"
    elif sa_json:
        try:
            data = json.loads(sa_json.strip())
            result["json_parse"] = "OK — project: " + data.get("project_id", "?")
        except Exception as e:
            result["json_parse"] = f"FAILED: {e}"
    db = get_db()
    result["push_tokens_count"] = db.push_tokens.count_documents({})
    return jsonify(result)

# ── Image upload for article body ─────────────────────────────────────────────
@admin_bp.route("/upload-image", methods=["POST"])
@login_required
def upload_image():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    f = request.files["file"]
    if not f or not f.filename:
        return jsonify({"error": "Empty file"}), 400
    try:
        cloudinary.config(
            cloud_name=current_app.config["CLOUDINARY_CLOUD_NAME"],
            api_key=current_app.config["CLOUDINARY_API_KEY"],
            api_secret=current_app.config["CLOUDINARY_API_SECRET"]
        )
        result = cloudinary.uploader.upload(
            f, folder="filmifire/body", quality="auto", fetch_format="auto"
        )
        return jsonify({"url": result.get("secure_url", "")})
    except Exception as e:
        return jsonify({"error": str(e)}), 500