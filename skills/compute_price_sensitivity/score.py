import json
import sqlite3, sys

PRICE_SIGNALS = [
    '₹', 'rs.', 'rupee', 'rupees', 'expensive', 'costly',
    'worth it', 'overpriced', 'cheap', 'affordable',
    'price hike', 'family plan', 'prime included',
    'too much', 'value', 'subscription', 'monthly',
    'annual', 'yearly', 'plan', 'upgrade', 'cancel'
]

def compute_score(app_id):
    conn = sqlite3.connect('data/reviews.db')
    texts = [r[0].lower() for r in conn.execute(
        'SELECT text FROM reviews WHERE app_id=?', 
        (app_id,)).fetchall()]
    
    total = len(texts)
    if total == 0:
        print(f'[ERROR] No reviews found for {app_id}')
        return 0
        
    hits = sum(1 for t in texts 
               if any(s in t for s in PRICE_SIGNALS))
    score = round(hits / total, 2)
    
    # Breakdown
    signal_counts = {}
    for signal in PRICE_SIGNALS:
        count = sum(1 for t in texts if signal in t)
        if count > 0:
            signal_counts[signal] = count
    
    print(f'[PRICE SENSITIVITY] {app_id}')
    print(f'  Score: {score} ({hits}/{total} reviews contain price signals)')
    print(f'  Top signals: {dict(sorted(signal_counts.items(), key=lambda x: x[1], reverse=True)[:5])}')
    return score

if __name__ == '__main__':
    apps = ['netflix', 'prime', 'hotstar']
    scores = {}
    for app in apps:
        scores[app] = compute_score(app)
    print(f'\n[SUMMARY] Price Sensitivity Scores: {json.dumps(scores, indent=2)}')
