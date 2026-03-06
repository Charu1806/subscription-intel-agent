"""
server.py — Subscription Intel Dashboard Server
Serves dashboard.html, report.json, and proxies chat to Gemini.

Local:   python3 server.py
Railway: gunicorn server:app --bind 0.0.0.0:$PORT
"""

import os
import json
from flask import Flask, jsonify, request, send_from_directory
from google import genai

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_PATH = os.path.join(BASE_DIR, 'outputs', 'report.json')

client = genai.Client(api_key=os.environ.get('GOOGLE_API_KEY'))

@app.route('/')
def index():
    return send_from_directory(BASE_DIR, 'dashboard.html')

@app.route('/dashboard.html')
def dashboard():
    return send_from_directory(BASE_DIR, 'dashboard.html')

@app.route('/outputs/report.json')
def report():
    if not os.path.exists(REPORT_PATH):
        return jsonify({'error': 'report.json not found.'}), 404
    with open(REPORT_PATH) as f:
        return jsonify(json.load(f))

@app.route('/chat', methods=['POST'])
def chat():
    body = request.get_json()
    user_message = body.get('message', '').strip()
    selected_apps = body.get('apps', ['netflix', 'prime', 'hotstar'])
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    context_data = {}
    if os.path.exists(REPORT_PATH):
        with open(REPORT_PATH) as f:
            report_data = json.load(f)
        context_data = {
            'sentiment':         {a: report_data['sentiment'][a]         for a in selected_apps if a in report_data.get('sentiment', {})},
            'price_sensitivity': {a: report_data['price_sensitivity'][a] for a in selected_apps if a in report_data.get('price_sensitivity', {})},
            'themes':            {a: report_data['themes'][a]            for a in selected_apps if a in report_data.get('themes', {})},
            'executive_summary': report_data.get('executive_summary', ''),
            'total_reviews':     report_data.get('meta', {}).get('total_reviews', 0),
        }

    system_prompt = f"""You are CharuIntelBot, a sharp and concise AI analyst specialising in India's OTT subscription market.
You have access to Play Store review intelligence data for: {', '.join(selected_apps)}.
Data context: {json.dumps(context_data, indent=2)}
Guidelines:
- Be concise — 3-5 sentences max unless asked for detail
- Lead with the most surprising or actionable insight
- Always tie back to India market context
- Never make up numbers — only use data from the context above
"""
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=user_message,
            config={'system_instruction': system_prompt}
        )
        return jsonify({'reply': response.text})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'reply': f'Error: {str(e)}'}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    print(f'\n🦞 Subscription Intel — http://localhost:{port}\n')
    app.run(port=port, debug=False)
