import json, os
from google import genai

client = genai.Client(api_key=os.environ.get('GOOGLE_API_KEY'))

def generate_summary(comparison, scores, themes):
    prompt = f"""You are a McKinsey analyst writing for a CPO audience.
Analyze Netflix, Amazon Prime, and Hotstar subscription intelligence in India.

Comparison: {json.dumps(comparison, indent=2)}
Price sensitivity scores (0-1): {json.dumps(scores, indent=2)}
Theme data: {json.dumps(themes, indent=2)}

Write an executive summary with:
- 5-7 bullet strategic insights (non-obvious, India-specific)
- 2 monetization risks  
- 2 opportunity areas

Rules:
- Direct, exec-ready tone
- No fluff
- Each bullet max 2 lines
- Ground every insight in data"""

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f'[ERROR] {e}')
        return ""

if __name__ == '__main__':
    print(generate_summary({}, {"netflix": 0.12, "prime": 0.20, "hotstar": 0.11}, {}))
