import sqlite3, json, sys, os
from google import genai

client = genai.Client(api_key=os.environ.get('GOOGLE_API_KEY'))

THEME_BUCKETS = [
    'Pricing complaints',
    'Forced upgrade pressure', 
    'Storage limit frustration',
    'Sync/backup reliability',
    'Privacy concerns',
    'Value-for-money praise',
    'Ecosystem integration praise'
]

def extract_themes(app_id):
    conn = sqlite3.connect('data/reviews.db')
    rows = conn.execute(
        'SELECT text FROM reviews WHERE app_id=?', 
        (app_id,)).fetchall()
    
    texts = [r[0][:150] for r in rows]
    
    prompt = f"""You are analyzing app reviews for subscription intelligence.
Given these {len(texts)} reviews, classify them into theme buckets.
ONLY use these exact theme names: {json.dumps(THEME_BUCKETS)}
Return ONLY a JSON object with theme names as keys and counts as values.
Sort by count descending. Include only top 5.
No explanation. No markdown. Just raw JSON.
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
        themes = json.loads(text.strip())
        print(f'[THEMES] {app_id}: {json.dumps(themes, indent=2)}')
        return themes
    except Exception as e:
        print(f'[ERROR] {e}')
        return {}

if __name__ == '__main__':
    app = sys.argv[1] if len(sys.argv) > 1 else 'netflix'
    extract_themes(app)
