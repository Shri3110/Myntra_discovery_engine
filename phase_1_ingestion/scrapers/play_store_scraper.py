import os
import sys
import time
from google_play_scraper import reviews, Sort

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.s3_uploader import save_data

def scrape_play_store_live(limit=255):
    """
    Scrapes live reviews from Google Play Store for the Myntra App.
    """
    app_id = 'com.myntra.android'
    print(f"Fetching live Play Store reviews for {app_id}...")
    
    try:
        result, continuation_token = reviews(
            app_id,
            lang='en', # defaults to 'en'
            country='in', # defaults to 'us'
            sort=Sort.NEWEST, # defaults to Sort.NEWEST
            count=limit # defaults to 100
        )
        
        all_data = []
        for r in result:
            all_data.append({
                "source": "Play Store",
                "app": "Myntra",
                "id": r['reviewId'],
                "title": f"Play Store Review (Rating: {r['score']})",
                "text": r['content'],
                "rating": r['score'],
                "created_at": r['at'].timestamp() if r.get('at') else time.time()
            })
            
        print(f"Successfully scraped {len(all_data)} live Play Store reviews.")
        return all_data
        
    except Exception as e:
        print(f"Error scraping Play Store: {e}")
        return []

if __name__ == "__main__":
    print("Starting Live Play Store Scraper...")
    data = scrape_play_store_live()
    if data:
        save_data(data, "play_store_feedback")
