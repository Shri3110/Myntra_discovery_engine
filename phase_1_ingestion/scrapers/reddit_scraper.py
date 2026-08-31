import os
import sys
import requests
from datetime import datetime

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.s3_uploader import save_data

def scrape_reddit_live(limit=15):
    """
    Scrapes live Reddit posts from r/IndianFashionAddicts using their open JSON endpoint.
    Bypasses the need for an official API key.
    """
    url = "https://www.reddit.com/r/IndianFashionAddicts/search.json?q=myntra&restrict_sr=1&sort=new"
    headers = {
        'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print(f"Fetching live data from {url}...")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        posts = data.get('data', {}).get('children', [])[:limit]
        
        all_data = []
        for post in posts:
            post_data = post['data']
            all_data.append({
                "source": "Reddit",
                "subreddit": post_data.get('subreddit'),
                "id": post_data.get('id'),
                "title": post_data.get('title'),
                "text": post_data.get('selftext', ''),
                "url": f"https://reddit.com{post_data.get('permalink')}",
                "score": post_data.get('score'),
                "num_comments": post_data.get('num_comments'),
                "created_utc": post_data.get('created_utc'),
                "comments": [] # Skip comments to avoid extra API calls without token
            })
            
        print(f"Successfully scraped {len(all_data)} live Reddit posts.")
        return all_data
        
    except Exception as e:
        print(f"Error scraping Reddit: {e}")
        return []

if __name__ == "__main__":
    print("Starting Live Reddit Scraper...")
    data = scrape_reddit_live()
    if data:
        save_data(data, "reddit_feedback")

