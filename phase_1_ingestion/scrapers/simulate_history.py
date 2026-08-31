import os
import sys
import time
import json
from datetime import datetime, timedelta
from google_play_scraper import reviews, Sort

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def generate_historical_data():
    app_id = 'com.myntra.android'
    print(f"Fetching 255 base reviews to duplicate for history...")
    
    result, _ = reviews(
        app_id,
        lang='en',
        country='in',
        sort=Sort.NEWEST,
        count=255
    )
    
    # We want to simulate the 20th, 21st, 22nd, and 23rd.
    # Today is 24th.
    base_date = datetime.now()
    
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
    os.makedirs(data_dir, exist_ok=True)
    
    for days_ago in [4, 3, 2, 1]:
        target_date = base_date - timedelta(days=days_ago)
        timestamp_str = target_date.strftime("%Y%m%d_%H%M%S")
        
        all_data = []
        for r in result:
            all_data.append({
                "source": "Play Store",
                "app": "Myntra",
                "id": f"{r['reviewId']}_{days_ago}", # unique ID
                "title": f"Play Store Review (Rating: {r['score']})",
                "text": r['content'],
                "rating": r['score'],
                "created_at": target_date.timestamp()
            })
            
        filename = f"play_store_feedback_{timestamp_str}.json"
        filepath = os.path.join(data_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)
            
        print(f"Saved {len(all_data)} historical reviews to {filename}")

if __name__ == "__main__":
    generate_historical_data()
