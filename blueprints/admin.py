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
    """Parse rating from form — returns int 1-5 or None"""
    try:
        r = int(val)
        return r if 1 <= r <= 5 else None
    except (TypeError, ValueError):
        return None

# ── Login / Logout ────────────────────────────────────────────────────────────
@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))
    if request.method == "POST":
        db = get_db()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").encode()
        user_doc = db.admins.find_one({"email": email})
        if user_doc and bcrypt.checkpw(password, user_doc["pw_hash"]):
            login_user(AdminUser(user_doc))
            return redirect(url_for("admin.dashboard"))
        flash("Invalid email or password.", "error")
    return render_template("admin/login.html")

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
        # Review fields
        rating = parse_rating(request.form.get("rating", ""))
        movie_name = request.form.get("movie_name", "").strip()

        # Handle image upload
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
        # Review fields
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

# ── Create first admin (run once, then remove this route) ────────────────────
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

# ── Image upload for article body (Quill editor) ──────────────────────────────
@admin_bp.route("/upload-image", methods=["POST"])
@login_required
def upload_image():
    from flask import jsonify
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
            f,
            folder="filmifire/body",
            quality="auto",
            fetch_format="auto"
        )
        url = result.get("secure_url", "")
        return jsonify({"url": url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500