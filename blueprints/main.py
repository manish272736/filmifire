from flask import Blueprint, render_template, request, abort, jsonify, redirect, url_for, flash
from db import get_db
from bson import ObjectId
import re
import datetime

main_bp = Blueprint("main", __name__)

def fmt_date(dt):
    if not dt:
        return ""
    return dt.strftime("%d %B %Y").lstrip("0")

def relative_time(dt):
    if not dt:
        return ""
    now = datetime.datetime.utcnow()
    diff = now - dt
    seconds = int(diff.total_seconds())
    if seconds < 60:
        return "just now"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    days = hours // 24
    if days < 7:
        return f"{days} day{'s' if days != 1 else ''} ago"
    if days < 30:
        weeks = days // 7
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"
    if days < 365:
        months = days // 30
        return f"{months} month{'s' if months != 1 else ''} ago"
    years = days // 365
    return f"{years} year{'s' if years != 1 else ''} ago"

@main_bp.app_template_filter("fmtdate")
def fmtdate_filter(dt):
    return fmt_date(dt)

@main_bp.app_template_filter("reltime")
def reltime_filter(dt):
    return relative_time(dt)

def smart_time(article):
    """Shows Updated X ago if updated more than 1hr after publish, else published time"""
    updated = article.get('updated_at')
    published = article.get('published_at')
    if updated and published:
        diff = (updated - published).total_seconds()
        if diff > 3600:
            return ('updated', relative_time(updated))
    return ('published', relative_time(published) if published else 'Draft')

@main_bp.app_template_filter("smarttime")
def smarttime_filter(article):
    return smart_time(article)

@main_bp.app_template_filter("cardtime")
def cardtime_filter(article):
    """For cards — shows updated time if updated, else published time"""
    updated = article.get('updated_at')
    published = article.get('published_at')
    if updated and published:
        diff = (updated - published).total_seconds()
        if diff > 3600:
            return '🔄 ' + relative_time(updated)
    return relative_time(published) if published else 'Draft'



# ── Homepage ──────────────────────────────────────────────────────────────────
@main_bp.route("/")
def index():
    db = get_db()
    pinned = list(db.articles.find(
        {"status": "published", "archived": {"$ne": True}, "pinned": True},
        sort=[("published_at", -1)]
    ))
    pinned_ids = [a["_id"] for a in pinned]
    remaining_limit = max(0, 15 - len(pinned))
    rest = list(db.articles.find(
        {"status": "published", "archived": {"$ne": True}, "_id": {"$nin": pinned_ids}},
        sort=[("published_at", -1)],
        limit=remaining_limit
    ))
    latest = pinned + rest
    trending = list(db.articles.find(
        {"status": "published", "archived": {"$ne": True}},
        sort=[("views", -1)],
        limit=5
    ))
    latest_news = list(db.articles.find(
        {"status": "published", "archived": {"$ne": True}, "category": "news"},
        sort=[("published_at", -1)],
        limit=8
    ))
    slider_articles = list(db.articles.find(
        {"status": "published", "archived": {"$ne": True}, "carousel": True},
        sort=[("published_at", -1)],
        limit=8
    ))
    photo_articles = list(db.articles.find(
        {"status": "published", "archived": {"$ne": True}, "category": "photos"},
        sort=[("published_at", -1)],
        limit=4
    ))
    return render_template("index.html", latest=latest, trending=trending, latest_news=latest_news, slider_articles=slider_articles, photo_articles=photo_articles)

# ── Article page ──────────────────────────────────────────────────────────────
@main_bp.route("/article/<slug>")
def article(slug):
    db = get_db()
    art = db.articles.find_one({"slug": slug, "status": "published"})
    if not art:
        abort(404)
    db.articles.update_one({"_id": art["_id"]}, {"$inc": {"views": 1}})
    related = list(db.articles.find(
        {
            "status": "published",
            "archived": {"$ne": True},
            "category": art["category"],
            "_id": {"$ne": art["_id"]}
        },
        sort=[("published_at", -1)],
        limit=4
    ))
    latest_news = list(db.articles.find(
        {"status": "published", "archived": {"$ne": True}, "category": "news"},
        sort=[("published_at", -1)],
        limit=6
    ))
    photo_articles = list(db.articles.find(
        {"status": "published", "archived": {"$ne": True}, "category": "photos"},
        sort=[("published_at", -1)],
        limit=6
    ))
    trending = list(db.articles.find(
        {"status": "published", "archived": {"$ne": True}},
        sort=[("views", -1)],
        limit=5
    ))
    return render_template("article.html", article=art, related=related,
                           latest_news=latest_news, photo_articles=photo_articles,
                           trending=trending)

# ── All articles page ─────────────────────────────────────────────────────────
@main_bp.route("/articles")
def all_articles():
    db = get_db()
    page = request.args.get("page", 1, type=int)
    cat = request.args.get("cat", "")
    per_page = 12
    skip = (page - 1) * per_page
    query = {"status": "published", "archived": {"$ne": True}}
    if cat:
        query["category"] = cat
    total = db.articles.count_documents(query)
    articles = list(db.articles.find(
        query,
        sort=[("published_at", -1)],
        skip=skip,
        limit=per_page
    ))
    total_pages = (total + per_page - 1) // per_page
    from config import Config
    photo_articles = list(db.articles.find(
        {"status": "published", "archived": {"$ne": True}, "category": "photos"},
        sort=[("published_at", -1)], limit=6
    ))
    latest_news = list(db.articles.find(
        {"status": "published", "archived": {"$ne": True}, "category": "news"},
        sort=[("published_at", -1)], limit=6
    ))
    trending = list(db.articles.find(
        {"status": "published", "archived": {"$ne": True}},
        sort=[("views", -1)], limit=5
    ))
    return render_template("all_articles.html",
        articles=articles,
        page=page,
        total_pages=total_pages,
        total=total,
        current_cat=cat,
        categories=Config.CATEGORIES,
        photo_articles=photo_articles,
        latest_news=latest_news,
        trending=trending
    )

# ── Category page ─────────────────────────────────────────────────────────────
@main_bp.route("/category/<slug>")
def category(slug):
    db = get_db()
    page = request.args.get("page", 1, type=int)
    per_page = 12
    skip = (page - 1) * per_page
    query = {"status": "published", "category": slug, "archived": {"$ne": True}}
    total = db.articles.count_documents(query)
    articles = list(db.articles.find(
        query,
        sort=[("published_at", -1)],
        skip=skip,
        limit=per_page
    ))
    total_pages = (total + per_page - 1) // per_page
    photo_articles = list(db.articles.find(
        {"status": "published", "archived": {"$ne": True}, "category": "photos"},
        sort=[("published_at", -1)], limit=6
    ))
    latest_news = list(db.articles.find(
        {"status": "published", "archived": {"$ne": True}, "category": "news"},
        sort=[("published_at", -1)], limit=6
    ))
    trending = list(db.articles.find(
        {"status": "published", "archived": {"$ne": True}},
        sort=[("views", -1)], limit=5
    ))
    return render_template("category.html",
        articles=articles,
        category_slug=slug,
        page=page,
        total_pages=total_pages,
        photo_articles=photo_articles,
        latest_news=latest_news,
        trending=trending
    )

# ── Search ────────────────────────────────────────────────────────────────────
@main_bp.route("/search")
def search():
    db = get_db()
    q = request.args.get("q", "").strip()
    results = []
    if q:
        pattern = re.compile(re.escape(q), re.IGNORECASE)
        results = list(db.articles.find(
            {
                "status": "published",
                "$or": [
                    {"title": {"$regex": pattern}},
                    {"excerpt": {"$regex": pattern}},
                    {"tags": {"$regex": pattern}},
                ]
            },
            sort=[("published_at", -1)],
            limit=20
        ))
    return render_template("search.html", results=results, query=q)

# ── Autocomplete API ──────────────────────────────────────────────────────────
@main_bp.route("/api/suggest")
def suggest():
    db = get_db()
    q = request.args.get("q", "").strip()
    if len(q) < 2:
        return jsonify([])
    pattern = re.compile(re.escape(q), re.IGNORECASE)
    articles = list(db.articles.find(
        {
            "status": "published",
            "archived": {"$ne": True},
            "$or": [
                {"title": {"$regex": pattern}},
                {"tags": {"$regex": pattern}},
            ]
        },
        {"title": 1, "slug": 1, "category": 1},
        limit=6
    ))
    return jsonify([{"title": a["title"], "slug": a["slug"], "category": a.get("category", "")} for a in articles])

# ── Tag page ──────────────────────────────────────────────────────────────────
@main_bp.route("/tag/<tag>")
def tag(tag):
    db = get_db()
    page = request.args.get("page", 1, type=int)
    per_page = 12
    skip = (page - 1) * per_page
    query = {"status": "published", "tags": tag, "archived": {"$ne": True}}
    total = db.articles.count_documents(query)
    articles = list(db.articles.find(query, sort=[("published_at", -1)], skip=skip, limit=per_page))
    total_pages = (total + per_page - 1) // per_page
    return render_template("tag.html", articles=articles, tag=tag, page=page, total_pages=total_pages)

# ── Static pages ──────────────────────────────────────────────────────────────
@main_bp.route("/about")
def about():
    return render_template("about.html")

@main_bp.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        subject = request.form.get("subject", "")
        message = request.form.get("message", "").strip()
        if name and email and message:
            db = get_db()
            db.messages.insert_one({
                "name": name, "email": email, "subject": subject, "message": message,
                "created_at": datetime.datetime.utcnow()
            })
            flash("Message sent! We'll get back to you within 24-48 hours.", "success")
        else:
            flash("Please fill in all fields.", "error")
        return redirect(url_for("main.contact"))
    return render_template("contact.html")

@main_bp.route("/privacy-policy")
def privacy():
    return render_template("privacy.html")

# ── Sitemap ───────────────────────────────────────────────────────────────────
@main_bp.route("/sitemap.xml")
def sitemap():
    from flask import make_response
    db = get_db()
    articles = list(db.articles.find({"status": "published"}, {"slug": 1, "published_at": 1}))
    xml = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    base = request.host_url.rstrip("/")
    xml.append(f"<url><loc>{base}/</loc></url>")
    for a in articles:
        loc = f"{base}/article/{a['slug']}"
        lastmod_dt = a.get("updated_at") or a.get("published_at")
        lastmod = lastmod_dt.strftime("%Y-%m-%d") if lastmod_dt else ""
        xml.append(f"<url><loc>{loc}</loc><lastmod>{lastmod}</lastmod></url>")
    xml.append("</urlset>")
    resp = make_response("\n".join(xml))
    resp.headers["Content-Type"] = "application/xml"
    return resp