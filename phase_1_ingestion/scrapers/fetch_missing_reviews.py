import os
import sys
import json
from datetime import datetime
from google_play_scraper import reviews, Sort

def fetch_missing():
    app_id = 'com.myntra.android'
    print("Fetching up to 10000 newest reviews...")
    
    result, _ = reviews(
        app_id,
        lang='en',
        country='in',
        sort=Sort.NEWEST,
        count=10000
    )
    
    filtered_data = []
    for r in result:
        review_date = r.get('at')
        filtered_data.append({
            "source": "Play Store",
            "app": "Myntra",
            "id": r['reviewId'],
            "title": f"Play Store Review (Rating: {r['score']})",
            "text": r['content'],
            "rating": r['score'],
            "created_at": review_date.timestamp() if review_date else 0
        })
            
    print(f"Found {len(filtered_data)} reviews.")
    
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
    os.makedirs(data_dir, exist_ok=True)
    
    # Save them all in one big file for the cleaner
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"play_store_feedback_bulk_{timestamp}.json"
    filepath = os.path.join(data_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(filtered_data, f, indent=2, ensure_ascii=False)
        
    print(f"Saved to {filepath}")

if __name__ == "__main__":
    fetch_missing()
