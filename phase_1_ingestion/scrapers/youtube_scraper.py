import os
import sys
import time
from itertools import islice
from youtube_comment_downloader import YoutubeCommentDownloader, SORT_BY_RECENT

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.s3_uploader import save_data

def scrape_youtube_live(limit=85):
    """
    Scrapes live comments from recent Myntra haul videos.
    Bypasses official YouTube API.
    """
    # Sample video IDs (recent Myntra hauls/reviews)
    video_urls = [
        "https://www.youtube.com/watch?v=k3Yk6Rj3KxA", 
        "https://www.youtube.com/watch?v=T_7bQ1WJ6xM"
    ]
    
    print(f"Fetching live YouTube comments from {len(video_urls)} videos...")
    downloader = YoutubeCommentDownloader()
    all_data = []
    
    try:
        for url in video_urls:
            comments = downloader.get_comments_from_url(url, sort_by=SORT_BY_RECENT)
            
            for comment in islice(comments, limit):
                all_data.append({
                    "source": "YouTube",
                    "video_id": url.split('v=')[-1],
                    "id": comment['cid'],
                    "author": comment['author'],
                    "text": comment['text'],
                    "likes": int(comment['votes']) if str(comment['votes']).isdigit() else 0,
                    "created_at": time.time()
                })
                
        print(f"Successfully scraped {len(all_data)} live YouTube comments.")
        return all_data
        
    except Exception as e:
        print(f"Error scraping YouTube: {e}")
        return []

if __name__ == "__main__":
    print("Starting Live YouTube Scraper...")
    data = scrape_youtube_live()
    if data:
        save_data(data, "youtube_feedback")
