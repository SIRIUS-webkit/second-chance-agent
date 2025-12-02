"""
Agent 1 - Scout
Monitors Google News RSS for LinkedIn layoff posts and extracts state information
"""
import os
import re
import time
import feedparser
import schedule
from datetime import datetime
from dotenv import load_dotenv
from utils.shared_state import append_to_shared_state
import subprocess

load_dotenv()


def extract_state_from_text(text: str) -> str:
    """
    Extracts state abbreviation from text using regex patterns.
    
    Args:
        text: Text to search for state abbreviation
    
    Returns:
        Two-letter state abbreviation or "CA" as default
    """
    # State abbreviations
    states = [
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
        "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
        "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
        "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
        "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
    ]
    
    # Pattern 1: "in CA", "from NY", "based in TX"
    pattern1 = r'\b(?:in|from|based in|located in|living in)\s+([A-Z]{2})\b'
    match = re.search(pattern1, text, re.IGNORECASE)
    if match:
        state = match.group(1).upper()
        if state in states:
            return state
    
    # Pattern 2: State names followed by abbreviation
    state_names = {
        "california": "CA", "new york": "NY", "texas": "TX", "florida": "FL",
        "illinois": "IL", "pennsylvania": "PA", "ohio": "OH", "georgia": "GA",
        "north carolina": "NC", "michigan": "MI", "new jersey": "NJ",
        "virginia": "VA", "washington": "WA", "arizona": "AZ", "massachusetts": "MA",
        "tennessee": "TN", "indiana": "IN", "missouri": "MO", "maryland": "MD",
        "wisconsin": "WI", "colorado": "CO", "minnesota": "MN", "south carolina": "SC",
        "alabama": "AL", "louisiana": "LA", "kentucky": "KY", "oregon": "OR",
        "oklahoma": "OK", "connecticut": "CT", "utah": "UT", "iowa": "IA",
        "nevada": "NV", "arkansas": "AR", "mississippi": "MS", "kansas": "KS",
        "new mexico": "NM", "nebraska": "NE", "west virginia": "WV", "idaho": "ID",
        "hawaii": "HI", "new hampshire": "NH", "maine": "ME", "montana": "MT",
        "rhode island": "RI", "delaware": "DE", "south dakota": "SD", "north dakota": "ND",
        "alaska": "AK", "vermont": "VT", "wyoming": "WY"
    }
    
    text_lower = text.lower()
    for state_name, abbrev in state_names.items():
        if state_name in text_lower:
            return abbrev
    
    # Default to CA if no state found
    return "CA"


def fetch_linkedin_layoff_posts() -> list:
    """
    Fetches LinkedIn layoff posts from Google News RSS feed.
    
    Returns:
        List of dictionaries with post data
    """
    # Google News RSS URL for LinkedIn posts about layoffs
    rss_url = "https://news.google.com/rss/search?q=site:linkedin.com/posts+%22laid+off%22&hl=en-US&gl=US&ceid=US:en"
    
    try:
        feed = feedparser.parse(rss_url)
        posts = []
        
        for entry in feed.entries[:10]:  # Limit to 10 most recent
            title = entry.get('title', '')
            link = entry.get('link', '')
            published = entry.get('published', '')
            summary = entry.get('summary', '')
            
            # Extract LinkedIn post URL
            linkedin_match = re.search(r'https://www\.linkedin\.com/posts/[^\s]+', link)
            if linkedin_match:
                linkedin_url = linkedin_match.group(0)
            else:
                # Try to extract from summary
                linkedin_match = re.search(r'https://www\.linkedin\.com/posts/[^\s<]+', summary)
                linkedin_url = linkedin_match.group(0) if linkedin_match else link
            
            # Extract state
            full_text = f"{title} {summary}"
            state = extract_state_from_text(full_text)
            
            posts.append({
                "title": title,
                "linkedin_url": linkedin_url,
                "published": published,
                "summary": summary,
                "state": state,
                "full_text": full_text
            })
        
        return posts
    
    except Exception as e:
        print(f"Error fetching RSS feed: {e}")
        return []


def process_new_posts():
    """
    Processes new LinkedIn layoff posts and triggers Agent 2 (Caseworker)
    """
    print(f"[Scout] Running at {datetime.utcnow().isoformat()}")
    
    posts = fetch_linkedin_layoff_posts()
    print(f"[Scout] Found {len(posts)} posts")
    
    # Read existing entries to avoid duplicates
    from utils.shared_state import read_shared_state
    existing_urls = {entry.get("linkedin_url") for entry in read_shared_state()}
    
    new_posts = [p for p in posts if p["linkedin_url"] not in existing_urls]
    print(f"[Scout] {len(new_posts)} new posts to process")
    
    for post in new_posts:
        # Append to shared state
        entry = {
            "linkedin_url": post["linkedin_url"],
            "state": post["state"],
            "post_text": post["full_text"],
            "title": post["title"],
            "published": post["published"],
            "status": "pending",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if append_to_shared_state(entry):
            print(f"[Scout] Added entry for {post['state']}: {post['linkedin_url']}")
            
            # Trigger Agent 2 (Caseworker)
            try:
                # Run caseworker agent
                subprocess.Popen(
                    ["python", "agents/caseworker.py", "--url", post["linkedin_url"]],
                    cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                )
                print(f"[Scout] Triggered Caseworker for {post['linkedin_url']}")
            except Exception as e:
                print(f"[Scout] Error triggering Caseworker: {e}")


def run_scout():
    """Main function to run Scout agent"""
    print("Starting Scout Agent...")
    print("Monitoring LinkedIn layoff posts every 30 minutes")
    
    # Schedule to run every 30 minutes
    schedule.every(30).minutes.do(process_new_posts)
    
    # Run immediately on start
    process_new_posts()
    
    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


if __name__ == "__main__":
    run_scout()

