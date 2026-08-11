import datetime
import re
from bson import ObjectId
from flask import (
    Blueprint,
    abort,
    flash,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
)

from config import Config
from db import get_active_trackers, get_db, get_tracker_by_slug
from tmdb_service import search_tmdb_movie

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
    """Shows Updated X ago if updated more than 1hr after publish, else published time."""
    updated = article.get("updated_at")
    published = article.get("published_at")
    if updated and published:
        diff = (updated - published).total_seconds()
        if diff > 3600:
            return ("updated", relative_time(updated))
    return ("published", relative_time(published) if published else "Draft")


@main_bp.app_template_filter("smarttime")
def smarttime_filter(article):
    return smart_time(article)


@main_bp.app_template_filter("cardtime")
def cardtime_filter(article):
    """For cards — shows updated time if updated more than 1hr after publish."""
    updated = article.get("updated_at")
    published = article.get("published_at")
    if updated and published:
        diff = (updated - published).total_seconds()
        if diff > 3600:
            return "Updated " + relative_time(updated)
    return relative_time(published) if published else "Draft"


# ── Homepage ──────────────────────────────────────────────────────────────────
@main_bp.route("/")
def index():
    db = get_db()
    pinned = list(
        db.articles.find(
            {
                "status": "published",
                "archived": {"$ne": True},
                "pinned": True,
                "category": {"$nin": ["photos", "box-office", "reviews"]},
            },
            sort=[("published_at", -1)],
        )
    )
    pinned_ids = [a["_id"] for a in pinned]
    remaining_limit = max(0, 12 - len(pinned))
    rest = list(
        db.articles.find(
            {
                "status": "published",
                "archived": {"$ne": True},
                "_id": {"$nin": pinned_ids},
                "category": {"$nin": ["photos", "box-office", "reviews"]},
            },
            sort=[("published_at", -1)],
            limit=remaining_limit,
        )
    )
    latest = pinned + rest
    week_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)
    trending = list(
        db.articles.find(
            {
                "status": "published",
                "archived": {"$ne": True},
                "published_at": {"$gte": week_ago},
            },
            sort=[("views", -1)],
            limit=5,
        )
    )
    if len(trending) < 5:
        existing_ids = [a["_id"] for a in trending]
        fallback = list(
            db.articles.find(
                {
                    "status": "published",
                    "archived": {"$ne": True},
                    "_id": {"$nin": existing_ids},
                },
                sort=[("views", -1)],
                limit=5 - len(trending),
            )
        )
        trending += fallback

    latest_news = list(
        db.articles.find(
            {"status": "published", "archived": {"$ne": True}, "category": "news"},
            sort=[("published_at", -1)],
            limit=8,
        )
    )
    slider_articles = list(
        db.articles.find(
            {"status": "published", "archived": {"$ne": True}, "carousel": True},
            sort=[("published_at", -1)],
            limit=8,
        )
    )
    photo_articles = list(
        db.articles.find(
            {"status": "published", "archived": {"$ne": True}, "category": "photos"},
            sort=[("published_at", -1)],
            limit=6,
        )
    )
    reviews_articles = list(
        db.articles.find(
            {"status": "published", "archived": {"$ne": True}, "category": "reviews"},
            sort=[("published_at", -1)],
            limit=10,
        )
    )

    # Get all active box office movie trackers for the homepage
    trackers = get_active_trackers()

    return render_template(
        "index.html",
        latest=latest,
        trending=trending,
        latest_news=latest_news,
        slider_articles=slider_articles,
        photo_articles=photo_articles,
        trackers=trackers,
        reviews_articles=reviews_articles,
    )


# ── Box Office Hub & Dynamic Live Trackers ────────────────────────────────────
@main_bp.route("/box-office/")
@main_bp.route("/box-office")
def box_office_hub():
    """Hub page displaying all movies currently being tracked."""
    trackers = get_active_trackers()
    return render_template("tracker_hub.html", trackers=trackers)


@main_bp.route("/box-office/<slug>/")
@main_bp.route("/box-office/<slug>")
def tracker_detail(slug):
    """Dynamic live tracker page for a specific movie."""
    movie = get_tracker_by_slug(slug)
    if not movie:
        abort(404)
    return render_template("tracker_detail.html", movie=movie)


# ── Article page ──────────────────────────────────────────────────────────────
@main_bp.route("/article/<slug>")
def article(slug):
    db = get_db()
    art = db.articles.find_one({"slug": slug, "status": "published"})
    if not art:
        abort(404)
    db.articles.update_one({"_id": art["_id"]}, {"$inc": {"views": 1}})

    # Multi-tag relevance score first
    article_tags = art.get("tags", [])
    related = []
    if article_tags:
        tag_matches = list(
            db.articles.find(
                {
                    "status": "published",
                    "archived": {"$ne": True},
                    "_id": {"$ne": art["_id"]},
                    "tags": {"$in": article_tags},
                },
                sort=[("published_at", -1)],
                limit=8,
            )
        )

        def tag_score(a):
            return len(set(a.get("tags", [])).intersection(set(article_tags)))

        tag_matches.sort(key=tag_score, reverse=True)
        related = tag_matches[:4]

    # Fill remaining slots with same-category articles
    if len(related) < 4:
        existing_ids = [r["_id"] for r in related] + [art["_id"]]
        cat_extras = list(
            db.articles.find(
                {
                    "status": "published",
                    "archived": {"$ne": True},
                    "category": art["category"],
                    "_id": {"$nin": existing_ids},
                },
                sort=[("published_at", -1)],
                limit=4 - len(related),
            )
        )
        related += cat_extras

    latest_news = list(
        db.articles.find(
            {"status": "published", "archived": {"$ne": True}, "category": "news"},
            sort=[("published_at", -1)],
            limit=6,
        )
    )
    photo_articles = list(
        db.articles.find(
            {"status": "published", "archived": {"$ne": True}, "category": "photos"},
            sort=[("published_at", -1)],
            limit=6,
        )
    )
    week_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)
    trending = list(
        db.articles.find(
            {
                "status": "published",
                "archived": {"$ne": True},
                "published_at": {"$gte": week_ago},
            },
            sort=[("views", -1)],
            limit=5,
        )
    )
    if len(trending) < 5:
        existing_ids = [a["_id"] for a in trending]
        fallback = list(
            db.articles.find(
                {
                    "status": "published",
                    "archived": {"$ne": True},
                    "_id": {"$nin": existing_ids},
                },
                sort=[("views", -1)],
                limit=5 - len(trending),
            )
        )
        trending += fallback

    return render_template(
        "article.html",
        article=art,
        related=related,
        latest_news=latest_news,
        photo_articles=photo_articles,
        trending=trending,
    )


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
    articles = list(
        db.articles.find(
            query,
            sort=[("published_at", -1)],
            skip=skip,
            limit=per_page,
        )
    )
    total_pages = (total + per_page - 1) // per_page
    photo_articles = list(
        db.articles.find(
            {"status": "published", "archived": {"$ne": True}, "category": "photos"},
            sort=[("published_at", -1)],
            limit=6,
        )
    )
    latest_news = list(
        db.articles.find(
            {"status": "published", "archived": {"$ne": True}, "category": "news"},
            sort=[("published_at", -1)],
            limit=6,
        )
    )
    trending = list(
        db.articles.find(
            {"status": "published", "archived": {"$ne": True}},
            sort=[("views", -1)],
            limit=5,
        )
    )
    return render_template(
        "all_articles.html",
        articles=articles,
        page=page,
        total_pages=total_pages,
        total=total,
        current_cat=cat,
        categories=Config.CATEGORIES,
        photo_articles=photo_articles,
        latest_news=latest_news,
        trending=trending,
    )


# ── Category page ─────────────────────────────────────────────────────────────
@main_bp.route("/category/<slug>/")
@main_bp.route("/category/<slug>")
def category(slug):
    # 301 Redirect old box-office category path directly to live hub
    if slug == "box-office":
        return redirect("/box-office/", code=301)

    db = get_db()
    page = request.args.get("page", 1, type=int)
    per_page = 12
    skip = (page - 1) * per_page
    query = {"status": "published", "category": slug, "archived": {"$ne": True}}
    total = db.articles.count_documents(query)
    articles = list(
        db.articles.find(
            query,
            sort=[("published_at", -1)],
            skip=skip,
            limit=per_page,
        )
    )
    total_pages = (total + per_page - 1) // per_page
    photo_articles = list(
        db.articles.find(
            {"status": "published", "archived": {"$ne": True}, "category": "photos"},
            sort=[("published_at", -1)],
            limit=6,
        )
    )
    latest_news = list(
        db.articles.find(
            {"status": "published", "archived": {"$ne": True}, "category": "news"},
            sort=[("published_at", -1)],
            limit=6,
        )
    )
    trending = list(
        db.articles.find(
            {"status": "published", "archived": {"$ne": True}},
            sort=[("views", -1)],
            limit=5,
        )
    )
    return render_template(
        "category.html",
        articles=articles,
        category_slug=slug,
        page=page,
        total_pages=total_pages,
        photo_articles=photo_articles,
        latest_news=latest_news,
        trending=trending,
    )


# ── Search ────────────────────────────────────────────────────────────────────
@main_bp.route("/search")
def search():
    db = get_db()
    q = request.args.get("q", "").strip()
    results = []
    if q:
        pattern = re.compile(re.escape(q), re.IGNORECASE)
        results = list(
            db.articles.find(
                {
                    "status": "published",
                    "$or": [
                        {"title": {"$regex": pattern}},
                        {"excerpt": {"$regex": pattern}},
                        {"tags": {"$regex": pattern}},
                    ],
                },
                sort=[("published_at", -1)],
                limit=20,
            )
        )
    return render_template("search.html", results=results, query=q)


# ── Autocomplete API ──────────────────────────────────────────────────────────
@main_bp.route("/api/suggest")
def suggest():
    db = get_db()
    q = request.args.get("q", "").strip()
    if len(q) < 2:
        return jsonify([])
    pattern = re.compile(re.escape(q), re.IGNORECASE)
    articles = list(
        db.articles.find(
            {
                "status": "published",
                "archived": {"$ne": True},
                "$or": [
                    {"title": {"$regex": pattern}},
                    {"tags": {"$regex": pattern}},
                ],
            },
            {"title": 1, "slug": 1, "category": 1},
            limit=6,
        )
    )
    return jsonify(
        [
            {"title": a["title"], "slug": a["slug"], "category": a.get("category", "")}
            for a in articles
        ]
    )


# ── Tag page ──────────────────────────────────────────────────────────────────
@main_bp.route("/tag/<tag>")
def tag(tag):
    db = get_db()
    page = request.args.get("page", 1, type=int)
    per_page = 12
    skip = (page - 1) * per_page
    query = {"status": "published", "tags": tag, "archived": {"$ne": True}}
    total = db.articles.count_documents(query)
    articles = list(
        db.articles.find(query, sort=[("published_at", -1)], skip=skip, limit=per_page)
    )
    total_pages = (total + per_page - 1) // per_page
    return render_template(
        "tag.html",
        articles=articles,
        tag=tag,
        page=page,
        total_pages=total_pages,
    )


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
            db.messages.insert_one(
                {
                    "name": name,
                    "email": email,
                    "subject": subject,
                    "message": message,
                    "created_at": datetime.datetime.utcnow(),
                }
            )
            flash(
                "Message sent! We'll get back to you within 24-48 hours.",
                "success",
            )
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
    db = get_db()
    base = request.host_url.rstrip("/")

    # Fetch articles
    articles = list(
        db.articles.find(
            {"status": "published", "archived": {"$ne": True}},
            {"slug": 1, "published_at": 1, "updated_at": 1},
        )
    )

    # Fetch dynamic box office trackers
    trackers = list(
        db.trackers.find(
            {},
            {"slug": 1, "last_updated": 1, "created_at": 1, "daily_collections": 1},
        )
    )

    xml = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]

    # 1. Core / Hub Pages
    core_pages = [
        {"loc": f"{base}/", "changefreq": "hourly", "priority": "1.0"},
        {"loc": f"{base}/box-office/", "changefreq": "hourly", "priority": "0.9"},
        {"loc": f"{base}/articles", "changefreq": "daily", "priority": "0.8"},
        {"loc": f"{base}/about", "changefreq": "monthly", "priority": "0.5"},
        {"loc": f"{base}/contact", "changefreq": "monthly", "priority": "0.5"},
        {"loc": f"{base}/privacy-policy", "changefreq": "monthly", "priority": "0.3"},
    ]

    for page in core_pages:
        xml.append("  <url>")
        xml.append(f"    <loc>{page['loc']}</loc>")
        xml.append(f"    <changefreq>{page['changefreq']}</changefreq>")
        xml.append(f"    <priority>{page['priority']}</priority>")
        xml.append("  </url>")

    # 2. Dynamic Live Box Office Trackers
    for movie in trackers:
        slug = movie.get("slug")
        if not slug:
            continue

        loc = f"{base}/box-office/{slug}/"
        
        # Calculate lastmod: last_updated -> created_at -> today
        lastmod_dt = movie.get("last_updated") or movie.get("created_at")
        
        if not lastmod_dt and movie.get("daily_collections"):
            try:
                last_day_str = movie["daily_collections"][-1].get("date")
                lastmod = last_day_str if last_day_str else ""
            except Exception:
                lastmod = ""
        elif isinstance(lastmod_dt, (datetime.datetime, datetime.date)):
            lastmod = lastmod_dt.strftime("%Y-%m-%d")
        else:
            lastmod = str(lastmod_dt)[:10] if lastmod_dt else ""

        xml.append("  <url>")
        xml.append(f"    <loc>{loc}</loc>")
        if lastmod:
            xml.append(f"    <lastmod>{lastmod}</lastmod>")
        xml.append("    <changefreq>daily</changefreq>")
        xml.append("    <priority>0.9</priority>")
        xml.append("  </url>")

    # 3. Regular Articles
    for a in articles:
        slug = a.get("slug")
        if not slug:
            continue

        loc = f"{base}/article/{slug}"
        lastmod_dt = a.get("updated_at") or a.get("published_at")
        
        if isinstance(lastmod_dt, (datetime.datetime, datetime.date)):
            lastmod = lastmod_dt.strftime("%Y-%m-%d")
        else:
            lastmod = str(lastmod_dt)[:10] if lastmod_dt else ""

        xml.append("  <url>")
        xml.append(f"    <loc>{loc}</loc>")
        if lastmod:
            xml.append(f"    <lastmod>{lastmod}</lastmod>")
        xml.append("    <changefreq>weekly</changefreq>")
        xml.append("    <priority>0.8</priority>")
        xml.append("  </url>")

    xml.append("</urlset>")

    resp = make_response("\n".join(xml))
    resp.headers["Content-Type"] = "application/xml"
    return resp


# ── TMDB Poster & Metadata Auto-Fetch API ─────────────────────────────────────
@main_bp.route("/api/fetch-movie")
def api_fetch_movie():
    query = request.args.get("q", "").strip()
    year = request.args.get("year", "").strip()
    
    if not query:
        return jsonify({"success": False, "message": "Missing movie title"}), 400

    movie_data = search_tmdb_movie(query, year=year)
    if movie_data:
        return jsonify({"success": True, "movie": movie_data})
    
    return jsonify({"success": False, "message": "No movie found on TMDB"}), 404