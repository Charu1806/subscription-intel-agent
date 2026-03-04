from google_play_scraper import reviews, Sort
import sqlite3, json, hashlib, datetime, sys

APP_IDS = {
    "netflix": "com.netflix.mediaclient",
    "prime": "com.amazon.avod.thirdpartyclient",
    "hotstar": "in.startv.hotstar"
}

def init_db():
    conn = sqlite3.connect('data/reviews.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS reviews 
        (review_id TEXT PRIMARY KEY, app_id TEXT, source TEXT, 
        rating INTEGER, text TEXT, timestamp DATETIME, 
        sentiment TEXT, themes JSON)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS app_metadata 
        (app_id TEXT PRIMARY KEY, last_scraped_at DATETIME)''')
    conn.commit()
    return conn

def already_scraped(app_id, conn):
    row = conn.execute(
        'SELECT last_scraped_at FROM app_metadata WHERE app_id=?', 
        (app_id,)).fetchone()
    return row is not None

def scrape_reviews(app_name, count=300):
    conn = init_db()
    if already_scraped(app_name, conn):
        print(f'[CACHE HIT] {app_name} — skipping scrape')
        return
    print(f'[SCRAPING] {app_name}...')
    result, _ = reviews(
        APP_IDS[app_name], 
        lang='en', 
        country='in', 
        sort=Sort.NEWEST, 
        count=count
    )
    for r in result:
        rid = hashlib.md5(r['reviewId'].encode()).hexdigest()
        conn.execute(
            'INSERT OR IGNORE INTO reviews VALUES (?,?,?,?,?,?,?,?)',
            (rid, app_name, 'playstore', r['score'], 
             r['content'], r['at'], None, None))
    conn.execute(
        'INSERT OR REPLACE INTO app_metadata VALUES (?,?)', 
        (app_name, datetime.datetime.now()))
    conn.commit()
    print(f'[DONE] {app_name}: {len(result)} reviews stored')

if __name__ == '__main__':
    app = sys.argv[1] if len(sys.argv) > 1 else 'netflix'
    scrape_reviews(app)
