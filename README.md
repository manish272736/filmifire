# FilmiFire 🎬

Pan-India movie news & box office editorial site.
Built with Flask + MongoDB + Render.

---

## Local Setup

```bash
# 1. Clone and enter project
git clone <your-repo-url>
cd filmifire

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment variables
cp .env.example .env
# Edit .env — add your MongoDB URI and other keys

# 5. Run the app
python app.py
```

Visit http://localhost:5000

---

## First-Time Admin Setup

1. Go to http://localhost:5000/admin/setup
2. Create your admin email + password
3. This route auto-disables once an admin exists

---

## Seed Sample Articles

```bash
python seed.py
```

Adds 6 sample articles (Dhurandhar, Pushpa 3, Coolie, KGF 3, Empuraan, Records).

---

## Project Structure

```
filmifire/
├── app.py                  # Flask app factory
├── config.py               # Config + categories
├── db.py                   # MongoDB connection + indexes
├── seed.py                 # Sample data
├── blueprints/
│   ├── main.py             # Public routes (home, article, category, search)
│   └── admin.py            # Admin routes (login, dashboard, editor)
├── templates/
│   ├── base.html           # Base layout (navbar, footer)
│   ├── index.html          # Homepage
│   ├── article.html        # Article detail
│   ├── category.html       # Category listing
│   ├── search.html         # Search results
│   └── admin/
│       ├── login.html      # Admin login
│       ├── dashboard.html  # Article management
│       └── editor.html     # Rich text article editor (Quill.js)
└── static/
    ├── css/style.css       # All styles
    └── js/main.js          # Scroll animations
```

---

## Deploying to Render

1. Push to GitHub
2. New Web Service on Render → connect repo
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app --workers 2 --bind 0.0.0.0:$PORT`
5. Add environment variables:
   - `MONGO_URI`
   - `SECRET_KEY`
   - `CLOUDINARY_CLOUD_NAME`
   - `CLOUDINARY_API_KEY`
   - `CLOUDINARY_API_SECRET`

---

## Adding Adsense Later

In `templates/article.html`, replace the ad slot divs with your Adsense `<ins>` tags:

```html
<!-- Replace this: -->
<div class="ad-slot ad-slot-banner">Ad · 728×90</div>

<!-- With your Adsense code: -->
<ins class="adsbygoogle" style="display:block" ...></ins>
```

---

## MongoDB Collections

| Collection | Purpose |
|---|---|
| `articles` | All articles — slug, body_html, category, tags, views, status |
| `admins` | Admin accounts — email + bcrypt hash |
