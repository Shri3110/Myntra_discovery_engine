import os
import sys
import time
from app_store_scraper import AppStore

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.s3_uploader import save_data

def scrape_app_store_live(limit=85):
    """
    Scrapes live reviews from Apple App Store for the Myntra App.
    """
    print("Fetching live App Store reviews for Myntra...")
    
    try:
        myntra = AppStore(country="in", app_name="myntra-fashion-shopping-app", app_id="907394059")
        myntra.review(how_many=limit)
        
        all_data = []
        for r in myntra.reviews:
            all_data.append({
                "source": "App Store",
                "app": "Myntra",
                "id": str(r.get('id', time.time())),
                "title": r.get('title', 'App Store Review'),
                "text": r.get('review', ''),
                "rating": r.get('rating', 0),
                "created_at": r.get('date').timestamp() if r.get('date') else time.time()
            })
            
        print(f"Successfully scraped {len(all_data)} live App Store reviews.")
        return all_data
        
    except Exception as e:
        print(f"Error scraping App Store: {e}")
        return []

if __name__ == "__main__":
    print("Starting Live App Store Scraper...")
    data = scrape_app_store_live()
    if data:
        save_data(data, "app_store_feedback")
