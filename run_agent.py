import json, os
from skills.get_playstore_reviews.scraper import scrape_reviews
from skills.analyze_sentiment.sentiment import run_sentiment
from skills.extract_subscription_themes.themes import extract_themes
from skills.compute_price_sensitivity.score import compute_score
from skills.compare_apps.compare import compare_apps
from skills.generate_executive_summary.summary import generate_summary

APPS = ['netflix', 'prime', 'hotstar']

def run_pipeline():
    print('=== SUBSCRIPTION INTEL AGENT STARTING ===\n')

    print('--- STEP 1: Scraping Play Store ---')
    for app in APPS:
        scrape_reviews(app)

    print('\n--- STEP 2: Sentiment Analysis ---')
    for app in APPS:
        run_sentiment(app)

    print('\n--- STEP 3: Themes + Price Sensitivity ---')
    app_results = {}
    themes_all = {}
    for app in APPS:
        themes = extract_themes(app)
        score = compute_score(app)
        app_results[app] = {
            'themes': themes,
            'price_sensitivity': score
        }
        themes_all[app] = themes

    print('\n--- STEP 4: Cross-App Comparison ---')
    comparison = compare_apps(app_results)
    print(json.dumps(comparison, indent=2))

    print('\n--- STEP 5: Executive Summary ---')
    scores = {app: app_results[app]['price_sensitivity'] for app in APPS}
    summary = generate_summary(comparison, scores, themes_all)

    os.makedirs('outputs', exist_ok=True)
    with open('outputs/report.md', 'w') as f:
        f.write('# Subscription Intelligence Report — India\n\n')
        f.write('## Price Sensitivity Scores\n')
        f.write(f'```json\n{json.dumps(scores, indent=2)}\n```\n\n')
        f.write('## Cross-App Comparison\n')
        f.write(f'```json\n{json.dumps(comparison, indent=2)}\n```\n\n')
        f.write('## Executive Summary\n\n')
        f.write(summary)

    print('\n=== DONE. Report saved to outputs/report.md ===')
    print(f'\nPrice Sensitivity: {json.dumps(scores)}')

if __name__ == '__main__':
    run_pipeline()
