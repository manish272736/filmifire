"""
Seed script — run once to populate sample articles.
Usage: python seed.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from db import get_db
import datetime

app = create_app()

ARTICLES = [
    {
        "title": "Dhurandhar Breaks Every Opening Weekend Record — Full Box Office Breakdown",
        "slug": "dhurandhar-opening-weekend-record-box-office",
        "excerpt": "Ranveer Singh's Dhurandhar has shattered the Bollywood opening weekend record with ₹312 Cr nett, surpassing Jawan's previous best. Here's every number.",
        "body_html": """
<p>Ranveer Singh starrer <strong>Dhurandhar</strong> has done the unthinkable — it has become the biggest Bollywood opener of all time, collecting an estimated <em>₹312 Cr nett</em> in its opening weekend alone.</p>

<h2>Day-by-Day Collections</h2>
<table>
  <thead><tr><th>Day</th><th>Collection (Nett India)</th><th>Footfalls</th></tr></thead>
  <tbody>
    <tr><td>Day 1 (Friday)</td><td>₹89 Cr</td><td>~1.1 Cr</td></tr>
    <tr><td>Day 2 (Saturday)</td><td>₹112 Cr</td><td>~1.4 Cr</td></tr>
    <tr><td>Day 3 (Sunday)</td><td>₹111 Cr</td><td>~1.38 Cr</td></tr>
    <tr><td><strong>Total OW</strong></td><td><strong>₹312 Cr</strong></td><td><strong>~3.88 Cr</strong></td></tr>
  </tbody>
</table>

<h2>Records Broken</h2>
<ul>
  <li>Biggest Bollywood opening day — surpassing Jawan (₹75 Cr)</li>
  <li>Biggest Bollywood opening weekend — surpassing Pathaan (₹302 Cr)</li>
  <li>Fastest Bollywood film to ₹300 Cr (3 days)</li>
  <li>Highest single-day collection for a Hindi film</li>
</ul>

<h2>What Powered This Run?</h2>
<p>The combination of a mass-action script, Ranveer Singh's career-best performance reviews, and a massive paid-preview strategy on Thursday night drove extraordinary footfalls. The film opened in <strong>5,200+ screens</strong> — the widest ever for a Hindi film.</p>

<blockquote>Advance booking crossed ₹80 Cr before release day — a number only Pathaan and Jawan had managed previously.</blockquote>

<h2>Can It Cross ₹1000 Cr?</h2>
<p>With a second-week hold looking strong and word-of-mouth firmly positive, trade analysts are projecting a final tally of <strong>₹850–950 Cr nett India</strong>. The ₹1000 Cr milestone remains ambitious but not impossible if the weekday hold is above 30%.</p>
        """,
        "category": "bollywood",
        "tags": ["Dhurandhar", "Ranveer Singh", "box office", "opening record", "Bollywood"],
        "status": "published",
        "featured": True,
        "views": 4821,
        "cover_img": "https://images.unsplash.com/photo-1478720568477-152d9b164e26?w=1200&q=80",
        "published_at": datetime.datetime(2025, 1, 15, 9, 0),
    },
    {
        "title": "Pushpa 3 Advance Booking Crosses ₹100 Cr — Allu Arjun Set to Shatter Own Record",
        "slug": "pushpa-3-advance-booking-100-cr-allu-arjun",
        "excerpt": "Pushpa 3 advance booking has crossed ₹100 Cr globally 10 days before release — here's how it compares to Pushpa 2's historic pre-sales.",
        "body_html": """
<p>The hype around <strong>Pushpa 3: The Rampage</strong> is at an all-time high. Advance booking has officially crossed <em>₹100 Cr globally</em> with 10 days still to go before release — a number only Pushpa 2 had achieved in its pre-sales run.</p>

<h2>Advance Booking Comparison</h2>
<table>
  <thead><tr><th>Film</th><th>Advance (10 days before)</th><th>Final Opening Day</th></tr></thead>
  <tbody>
    <tr><td>Pushpa: The Rise</td><td>₹18 Cr</td><td>₹24 Cr</td></tr>
    <tr><td>Pushpa 2: The Rule</td><td>₹85 Cr</td><td>₹164 Cr</td></tr>
    <tr><td>Pushpa 3: The Rampage</td><td>₹100 Cr+</td><td>TBD</td></tr>
  </tbody>
</table>

<h2>Why the Frenzy?</h2>
<p>Pushpa 2 delivered the biggest Hindi-dubbed opening in history and crossed <strong>₹1800 Cr</strong> worldwide. Pushpa 3 carries that momentum plus the unfinished confrontation between Pushpa Raj and Bhanwar Singh Shekhawat. The interval block of Pushpa 2 alone generated enough anticipation to fuel a year of speculation.</p>

<h2>Opening Day Projection</h2>
<p>Trade sources are projecting an opening day between <strong>₹180–210 Cr nett India</strong>, which would comfortably beat Pushpa 2's ₹164 Cr. A ₹200 Cr opening day for a Telugu film would be unprecedented.</p>
        """,
        "category": "tollywood",
        "tags": ["Pushpa 3", "Allu Arjun", "advance booking", "Tollywood", "box office"],
        "status": "published",
        "featured": False,
        "views": 3102,
        "cover_img": "https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=1200&q=80",
        "published_at": datetime.datetime(2025, 1, 12, 10, 30),
    },
    {
        "title": "Rajinikanth's Coolie vs His 10 Biggest Openers — Can It Top Jailer?",
        "slug": "rajinikanth-coolie-vs-biggest-openers-jailer",
        "excerpt": "As Coolie release approaches, we rank all of Rajinikanth's top opening-day collections and ask: can Coolie beat Jailer's ₹55 Cr Tamil Nadu opening?",
        "body_html": """
<p><strong>Coolie</strong> is shaping up to be one of Rajinikanth's biggest releases. Directed by Lokesh Kanagaraj, the film carries immense expectations. But can it top the numbers Jailer set in 2023?</p>

<h2>Rajinikanth's Top 5 Opening Days (Tamil Nadu)</h2>
<table>
  <thead><tr><th>Film</th><th>Year</th><th>TN Opening Day</th></tr></thead>
  <tbody>
    <tr><td>Jailer</td><td>2023</td><td>₹55 Cr</td></tr>
    <tr><td>Darbar</td><td>2020</td><td>₹34 Cr</td></tr>
    <tr><td>Petta</td><td>2019</td><td>₹28 Cr</td></tr>
    <tr><td>2.0</td><td>2018</td><td>₹45 Cr (all languages)</td></tr>
    <tr><td>Enthiran</td><td>2010</td><td>₹22 Cr</td></tr>
  </tbody>
</table>

<h2>The Lokesh Factor</h2>
<p>Lokesh Kanagaraj is arguably Tamil cinema's hottest director right now. His track record — Maanagaram, Master, Vikram, Leo — combined with Rajinikanth in mass-action mode is a combination that has sent advance booking into a frenzy.</p>

<blockquote>Coolie is tracking to open bigger than Jailer in all circuits except possibly Chennai multiplex, where Jailer had historic numbers.</blockquote>

<h2>Verdict</h2>
<p>Based on current trends, Coolie is projected to open at <strong>₹60–70 Cr in Tamil Nadu alone</strong>, which would set a new record for a Tamil film. The worldwide opening could challenge the ₹200 Cr mark.</p>
        """,
        "category": "kollywood",
        "tags": ["Coolie", "Rajinikanth", "Lokesh Kanagaraj", "Kollywood", "box office", "Jailer"],
        "status": "published",
        "featured": False,
        "views": 2788,
        "cover_img": "https://images.unsplash.com/photo-1485846234645-a62644f84728?w=1200&q=80",
        "published_at": datetime.datetime(2025, 1, 10, 8, 0),
    },
    {
        "title": "KGF Chapter 3 — Why the Delay, and What the Numbers Need to Be",
        "slug": "kgf-chapter-3-delay-box-office-expectations",
        "excerpt": "KGF Chapter 2 collected ₹1200 Cr worldwide. Three years later, Chapter 3 is still not in production. We break down the numbers it needs to justify the hype.",
        "body_html": """
<p>It has been over three years since <strong>KGF Chapter 2</strong> redrew the map of Indian cinema. With ₹1200 Cr worldwide and records that still stand today, the pressure on Chapter 3 is enormous. So why isn't it in production yet?</p>

<h2>The KGF Legacy in Numbers</h2>
<table>
  <thead><tr><th>Film</th><th>Budget</th><th>Worldwide Collection</th><th>ROI</th></tr></thead>
  <tbody>
    <tr><td>KGF Chapter 1</td><td>₹80 Cr</td><td>₹250 Cr</td><td>213%</td></tr>
    <tr><td>KGF Chapter 2</td><td>₹100 Cr</td><td>₹1200 Cr</td><td>1100%</td></tr>
    <tr><td>KGF Chapter 3</td><td>₹150 Cr (est.)</td><td>₹1500 Cr+ (target)</td><td>—</td></tr>
  </tbody>
</table>

<h2>Why the Delay?</h2>
<p>Director Prashanth Neel has been vocal about the scale of Chapter 3. The script reportedly involves a global canvas — multiple countries, a massive antagonist, and a conclusion to Rocky's arc. The VFX pipeline alone is estimated to take 18 months post-shoot.</p>

<p>Yash has also been selective about taking on the role again — he wants Chapter 3 to be definitive, not just a cash grab.</p>

<h2>What It Needs to Deliver</h2>
<p>For Chapter 3 to be considered a success, it needs to clear <strong>₹1500 Cr worldwide</strong>. Anything less will be seen as a step backward. The fan expectations are for a ₹2000 Cr film — a figure that only Baahubali 2 has crossed in Indian cinema history.</p>
        """,
        "category": "sandalwood",
        "tags": ["KGF Chapter 3", "Yash", "Prashanth Neel", "Sandalwood", "box office", "records"],
        "status": "published",
        "featured": False,
        "views": 1944,
        "cover_img": "https://images.unsplash.com/photo-1440404653325-ab127d49abc1?w=1200&q=80",
        "published_at": datetime.datetime(2025, 1, 8, 11, 0),
    },
    {
        "title": "Mohanlal's L2: Empuraan — The Most Expensive Malayalam Film Ever, Justified?",
        "slug": "mohanlal-l2-empuraan-budget-box-office-malayalam-record",
        "excerpt": "L2: Empuraan carries a ₹200 Cr budget — uncharted territory for Malayalam cinema. We examine whether the box office can support it.",
        "body_html": """
<p><strong>L2: Empuraan</strong>, the sequel to the critically acclaimed Lucifer, is being made at a scale Malayalam cinema has never seen. With a reported budget of <em>₹200 Cr</em>, it is already a landmark production before a single frame has been released.</p>

<h2>Malayalam Cinema's Biggest Budgets</h2>
<table>
  <thead><tr><th>Film</th><th>Year</th><th>Budget</th><th>Worldwide Collection</th></tr></thead>
  <tbody>
    <tr><td>L2: Empuraan</td><td>2025</td><td>₹200 Cr</td><td>TBD</td></tr>
    <tr><td>Lucifer</td><td>2019</td><td>₹25 Cr</td><td>₹200 Cr</td></tr>
    <tr><td>2018</td><td>2023</td><td>₹55 Cr</td><td>₹150 Cr</td></tr>
    <tr><td>Marco</td><td>2024</td><td>₹30 Cr</td><td>₹110 Cr</td></tr>
  </tbody>
</table>

<h2>The Challenge</h2>
<p>Malayalam cinema's traditional market — Kerala + diaspora — has a ceiling. Even the biggest hits rarely cross ₹200 Cr worldwide from the Malayalam version alone. Empuraan is banking on pan-India release with massive Hindi and Telugu dubs to justify the budget.</p>

<p>Mohanlal's pan-India appeal was validated by Lucifer's performance in Tamil Nadu and Karnataka. Empuraan, with Prithviraj Sukumaran's direction and a bigger canvas, is expected to expand that base significantly.</p>

<h2>Break-Even and Profit</h2>
<p>The film needs approximately <strong>₹450–500 Cr worldwide</strong> to be a clean hit after P&A costs. That would be 2.5× the highest-ever Malayalam film collection — a tall order, but not impossible given the franchise value.</p>
        """,
        "category": "mollywood",
        "tags": ["L2 Empuraan", "Mohanlal", "Prithviraj", "Mollywood", "Malayalam cinema", "box office"],
        "status": "published",
        "featured": False,
        "views": 1203,
        "cover_img": "https://images.unsplash.com/photo-1509347528160-9a9e33742cdb?w=1200&q=80",
        "published_at": datetime.datetime(2025, 1, 6, 9, 30),
    },
    {
        "title": "All-Time Box Office Records — Pan India Films That Changed the Game",
        "slug": "all-time-pan-india-box-office-records",
        "excerpt": "From Baahubali 2 to Pushpa 2, here is every pan-India box office record that has been set and broken in Indian cinema history.",
        "body_html": """
<p>Indian cinema has undergone a revolution in the last decade. Pan-India releases have redefined what blockbuster means. Here is the complete record list as it stands today.</p>

<h2>All-Time Worldwide Grossers (Indian Films)</h2>
<table>
  <thead><tr><th>Rank</th><th>Film</th><th>Year</th><th>Industry</th><th>Worldwide (₹ Cr)</th></tr></thead>
  <tbody>
    <tr><td>1</td><td>Baahubali 2</td><td>2017</td><td>Tollywood</td><td>₹1810 Cr</td></tr>
    <tr><td>2</td><td>KGF Chapter 2</td><td>2022</td><td>Sandalwood</td><td>₹1200 Cr</td></tr>
    <tr><td>3</td><td>Pushpa 2: The Rule</td><td>2024</td><td>Tollywood</td><td>₹1800 Cr+</td></tr>
    <tr><td>4</td><td>RRR</td><td>2022</td><td>Tollywood</td><td>₹1200 Cr</td></tr>
    <tr><td>5</td><td>Jawan</td><td>2023</td><td>Bollywood</td><td>₹1160 Cr</td></tr>
    <tr><td>6</td><td>Pathaan</td><td>2023</td><td>Bollywood</td><td>₹1060 Cr</td></tr>
    <tr><td>7</td><td>Animal</td><td>2023</td><td>Bollywood</td><td>₹920 Cr</td></tr>
    <tr><td>8</td><td>Kalki 2898 AD</td><td>2024</td><td>Tollywood</td><td>₹1000 Cr+</td></tr>
  </tbody>
</table>

<h2>Records That Still Stand</h2>
<ul>
  <li><strong>Biggest opening weekend ever:</strong> Pushpa 2 — ₹513 Cr worldwide</li>
  <li><strong>Fastest to ₹1000 Cr:</strong> Pushpa 2 — 6 days</li>
  <li><strong>Highest Hindi-dubbed gross:</strong> Pushpa 2 — ₹900 Cr+</li>
  <li><strong>Biggest South Indian opener:</strong> Kalki 2898 AD — ₹95 Cr Day 1</li>
  <li><strong>Longest theatrical run:</strong> Baahubali 2 — still running in select screens 8 years later</li>
</ul>

<h2>The New Benchmark</h2>
<p>Pushpa 2 has effectively set a new benchmark: <strong>₹1500 Cr worldwide</strong> is now the threshold for a "historic blockbuster" in Indian cinema. Any film aspiring to all-time greatness needs to clear that mark.</p>
        """,
        "category": "records",
        "tags": ["box office records", "Baahubali", "KGF", "Pushpa 2", "pan India", "all time"],
        "status": "published",
        "featured": False,
        "views": 5610,
        "cover_img": "https://images.unsplash.com/photo-1574267432553-4b4628081c31?w=1200&q=80",
        "published_at": datetime.datetime(2025, 1, 3, 7, 0),
    },
]


def run():
    with app.app_context():
        db = get_db()
        inserted = 0
        skipped = 0
        for art in ARTICLES:
            if db.articles.find_one({"slug": art["slug"]}):
                print(f"  skip  {art['slug']}")
                skipped += 1
                continue
            db.articles.insert_one(art)
            print(f"  added {art['slug']}")
            inserted += 1
        print(f"\nDone — {inserted} inserted, {skipped} skipped.")


if __name__ == "__main__":
    run()
