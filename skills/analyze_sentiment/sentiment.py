import sqlite3, json, sys, os
from google import genai

client = genai.Client(api_key=os.environ.get('GOOGLE_API_KEY'))

def run_sentiment(app_id):
    conn = sqlite3.connect('data/reviews.db')
    rows = conn.execute(
        'SELECT review_id, text FROM reviews WHERE app_id=? AND sentiment IS NULL',
        (app_id,)).fetchall()
    
    print(f'[SENTIMENT] Processing {len(rows)} reviews for {app_id} in 1 call...')
    
    # Send ALL reviews in one single API call
    texts = [{"id": i, "text": r[1][:200]} for i, r in enumerate(rows)]
    
    prompt = f"""Classify each review as positive, neutral, or negative.
Return ONLY a JSON array like: [{{"id": 0, "sentiment": "positive"}}, ...]
No explanation. No markdown. Just the raw JSON array.
Reviews: {json.dumps(texts)}"""

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        text = response.text.strip()
        if '```' in text:
            text = text.split('```')[1]
            if text.startswith('json'):
                text = text[4:]
        results = json.loads(text.strip())
        
        for res in results:
            conn.execute(
                'UPDATE reviews SET sentiment=? WHERE review_id=?',
                (res['sentiment'], rows[res['id']][0]))
        conn.commit()
        print(f'[DONE] {len(results)} reviews tagged for {app_id}')
        
    except Exception as e:
        print(f'[ERROR] {e}')

if __name__ == '__main__':
    app = sys.argv[1] if len(sys.argv) > 1 else 'netflix'
    run_sentiment(app)
