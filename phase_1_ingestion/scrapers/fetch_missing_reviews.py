import os
import sys
import json
from datetime import datetime
from google_play_scraper import reviews, Sort

def fetch_missing():
    app_id = 'com.myntra.android'
    print("Fetching up to 3000 newest reviews...")
    
    result, _ = reviews(
        app_id,
        lang='en',
        country='in',
        sort=Sort.NEWEST,
        count=3000
    )
    
    start_date = datetime(2026, 8, 26) # 26th to 30th (exclusive of 31st which is already fetched)
    end_date = datetime(2026, 8, 31)
    
    filtered_data = []
    for r in result:
        review_date = r.get('at')
        if review_date and start_date <= review_date < end_date:
            filtered_data.append({
                "source": "Play Store",
                "app": "Myntra",
                "id": r['reviewId'],
                "title": f"Play Store Review (Rating: {r['score']})",
                "text": r['content'],
                "rating": r['score'],
                "created_at": review_date.timestamp()
            })
            
    print(f"Found {len(filtered_data)} real reviews between Aug 26 and Aug 30.")
    
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
    os.makedirs(data_dir, exist_ok=True)
    
    # Save a chunk for each day to mimic daily scrapes
    # Just save them all in one big file for the cleaner
    filename = f"play_store_feedback_20260826_120000.json"
    filepath = os.path.join(data_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(filtered_data, f, indent=2, ensure_ascii=False)
        
    print(f"Saved to {filepath}")

if __name__ == "__main__":
    fetch_missing()
