from datetime import datetime, timezone
from app import create_app
from db import create_or_update_tracked_movie

app = create_app()

sample_movie = {
    "title": "Stree 2",
    "slug": "stree-2-box-office-collection",
    "poster_url": "/static/favicon-32x32.png",  # Update with your movie poster url
    "release_date": "2024-08-15",
    "budget": "60 Cr",
    "language": "Hindi",
    "verdict": "All Time Blockbuster",
    "status": "active",
    "target_club": 800,  # Goal target in Cr

    "totals": {
        "india_net": 598.90,
        "india_gross": 718.00,
        "overseas_gross": 140.00,
        "worldwide_gross": 858.00
    },

    "today_live": {
        "day_number": 25,
        "date": "2026-08-11",
        "current_estimate": 4.50,
        "advance_booking_gross": 1.85,
        "tickets_sold": 95000,
        "morning_occ": "18%",
        "afternoon_occ": "32%",
        "evening_occ": "55%",
        "night_occ": "—",
        "last_slot_updated": "Evening (07:00 PM)",
        "quick_summary": "Holding exceptionally well on 4th weekend with strong family footfalls."
    },

    "daily_breakdown": [
        {
            "day": 1,
            "date": "2024-08-15",
            "day_name": "Thursday",
            "india_net": 51.80,
            "worldwide_gross": 75.50,
            "occupancy": "75%",
            "status": "final"
        },
        {
            "day": 2,
            "date": "2024-08-16",
            "day_name": "Friday",
            "india_net": 31.40,
            "worldwide_gross": 46.00,
            "occupancy": "52%",
            "status": "final"
        }
    ],

    "created_at": datetime.now(timezone.utc),
    "last_updated": datetime.now(timezone.utc)
}

with app.app_context():
    create_or_update_tracked_movie(sample_movie)
    print("✅ Sample tracker document successfully added to MongoDB Atlas!")