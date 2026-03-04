import json, os
from google import genai

client = genai.Client(api_key=os.environ.get('GOOGLE_API_KEY'))

def compare_apps(app_results):
    prompt = f"""You are a senior product strategist analyzing subscription apps in India.
Given this data for 3 apps:
{json.dumps(app_results, indent=2)}

Generate a JSON object with exactly these keys:
- differentiation: list of 3 key differences between apps
- subscription_risk: list of top risk signal per app
- competitive_weaknesses: list of where each app loses users
- india_opportunities: list of 2 strategic opportunities in India

Be specific. Ground in the data. No generic statements.
Return ONLY raw JSON. No markdown. No explanation."""

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
        return json.loads(text.strip())
    except Exception as e:
        print(f'[ERROR] {e}')
        return {}

if __name__ == '__main__':
    dummy = {
        "netflix": {"themes": {"Pricing complaints": 34}, "price_sensitivity": 0.12},
        "prime": {"themes": {"Value-for-money praise": 28}, "price_sensitivity": 0.20},
        "hotstar": {"themes": {"Forced upgrade pressure": 41}, "price_sensitivity": 0.11}
    }
    result = compare_apps(dummy)
    print(json.dumps(result, indent=2))
