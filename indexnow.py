"""
IndexNow — instant Bing/Yahoo/Yandex indexing on article publish/update
Place this file at: indexnow.py (project root, same level as app.py)

Setup:
1. Go to https://www.bing.com/indexnow and generate a key
2. Replace INDEXNOW_KEY below with your actual key
3. Create a file named <your-key>.txt in static/ folder containing just the key
4. Add INDEXNOW_KEY to your .env file
"""

import requests
import os

INDEXNOW_KEY = os.environ.get("INDEXNOW_KEY", "43d0889e6360462c8980bb8875f15597")
SITE_URL = "https://filmifire.com"
INDEXNOW_ENDPOINT = "https://api.indexnow.org/indexnow"


def ping_indexnow(slug: str) -> bool:
    """
    Ping IndexNow for a single article URL.
    Call this after publishing or updating an article.
    Returns True on success, False on failure (never raises).
    """
    if not INDEXNOW_KEY:
        return False

    url = f"{SITE_URL}/article/{slug}"

    try:
        resp = requests.post(
            INDEXNOW_ENDPOINT,
            json={
                "host": "filmifire.com",
                "key": INDEXNOW_KEY,
                "keyLocation": f"{SITE_URL}/{INDEXNOW_KEY}.txt",
                "urlList": [url]
            },
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        return resp.status_code in (200, 202)
    except Exception:
        return False


def ping_indexnow_bulk(slugs: list) -> dict:
    """
    Ping IndexNow for multiple URLs at once.
    Used by the /admin/ping-indexnow-all route.
    Returns {"sent": int, "ok": bool}
    """
    if not INDEXNOW_KEY or not slugs:
        return {"sent": 0, "ok": False}

    urls = [f"{SITE_URL}/article/{s}" for s in slugs]

    try:
        resp = requests.post(
            INDEXNOW_ENDPOINT,
            json={
                "host": "filmifire.com",
                "key": INDEXNOW_KEY,
                "keyLocation": f"{SITE_URL}/{INDEXNOW_KEY}.txt",
                "urlList": urls
            },
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        return {"sent": len(urls), "ok": resp.status_code in (200, 202)}
    except Exception as e:
        return {"sent": 0, "ok": False, "error": str(e)}
