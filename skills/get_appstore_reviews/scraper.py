from app_store_scraper import AppStore
import sqlite3, hashlib, datetime, sys

APPS = {
    "netflix": {"app_id": "363590051", "name": "Netflix"},
    "prime": {"app_id": "545519333", "name": "Amazon Prime Video"},
    "hotstar": {"app_id": "1455056902", "name": "JioHotstar"}
}

def init_db():
    conn = sqlite3.connect("data/reviews.db")
    conn.execute("CREATE TABLE IF NOT EXISTS reviews (review_id TEXT PRIMARY KEY, app_id TEXT, source TEXT, rating INTEGER, text TEXT, timestamp DATETIME, sentiment TEXT, themes JSON)")
    conn.commit()
    return conn

def already_scraped(app_name, conn):
    row = conn.execute("SELECT last_scraped_at FROM app_metadata WHERE app_id=?", ("appstore_" + app_name,)).fetchone()
    return row is not None

def scrape_appstore(app_name, count=100):
    conn = init_db()
    if already_scraped(app_name, conn):
        print("[CACHE HIT] appstore_" + app_name + " skipping")
        return
    print("[SCRAPING AppStore] " + app_name)
    app_info = APPS[app_name]
    app = AppStore(country="in", app_name=app_info["name"], app_id=app_info["app_id"])
    app.review(how_many=count)
    stored = 0
    for r in app.reviews:
        rid = hashlib.md5(str(str(r.get("date","")) + r.get("userName","")).encode()).hexdigest()
        text = r.get("review", "")
        rating = r.get("rating", None)
        date = r.get("date", datetime.datetime.now())
        conn.execute("INSERT OR IGNORE INTO reviews VALUES (?,?,?,?,?,?,?,?)", (rid, app_name, "appstore", rating, text, date, None, None))
        stored += 1
    conn.execute("INSERT OR REPLACE INTO app_metadata VALUES (?,?)", ("appstore_" + app_name, datetime.datetime.now()))
    conn.commit()
    print("[DONE] AppStore " + app_name + ": " + str(stored) + " reviews stored")

if __name__ == "__main__":
    app = sys.argv[1] if len(sys.argv) > 1 else "netflix"
    scrape_appstore(app)
