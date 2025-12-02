"""
Agent 3 - Watchdog
Daily statistics and Twitter/X posting
"""
import os
import schedule
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from utils.shared_state import get_statistics
import tweepy

load_dotenv()


def post_to_twitter(message: str) -> dict:
    """
    Posts a message to Twitter/X using API v2.
    
    Args:
        message: Tweet text (max 280 characters)
    
    Returns:
        Dictionary with status and tweet ID
    """
    try:
        # Twitter API v2 credentials
        api_key = os.getenv("TWITTER_API_KEY")
        api_secret = os.getenv("TWITTER_API_SECRET")
        access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
        
        if not all([api_key, api_secret, access_token, access_token_secret]):
            return {
                "status": "error",
                "message": "Twitter API credentials not configured"
            }
        
        # Authenticate
        client = tweepy.Client(
            bearer_token=bearer_token,
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
            wait_on_rate_limit=True
        )
        
        # Post tweet
        response = client.create_tweet(text=message)
        
        return {
            "status": "success",
            "tweet_id": response.data['id'],
            "message": f"Tweet posted successfully: {response.data['id']}"
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error posting to Twitter: {str(e)}"
        }


def generate_daily_stats_tweet() -> str:
    """
    Generates a daily statistics tweet.
    
    Returns:
        Tweet text
    """
    stats = get_statistics()
    
    total_amount = stats["total_amount_unlocked"]
    total_rows = stats["total_rows"]
    
    # Format amount with commas
    amount_str = f"${total_amount:,.0f}" if total_amount >= 1000 else f"${total_amount:.2f}"
    
    tweet = (
        f"Yesterday Second-Chance-ADK helped {total_rows} laid-off workers "
        f"unlock an estimated {amount_str} in benefits they didn't know existed. "
        f"#AgentsForGood #AIForGood"
    )
    
    # Ensure tweet is within 280 character limit
    if len(tweet) > 280:
        # Truncate if needed
        tweet = tweet[:277] + "..."
    
    return tweet


def daily_stats_job():
    """
    Daily job that runs at 08:00 UTC to post statistics to Twitter.
    """
    print(f"[Watchdog] Running daily stats job at {datetime.utcnow().isoformat()}")
    
    # Get statistics
    stats = get_statistics()
    print(f"[Watchdog] Total amount unlocked: ${stats['total_amount_unlocked']:,.2f}")
    print(f"[Watchdog] Total cases processed: {stats['total_rows']}")
    
    # Generate and post tweet
    tweet_text = generate_daily_stats_tweet()
    print(f"[Watchdog] Tweet text: {tweet_text}")
    
    result = post_to_twitter(tweet_text)
    
    if result["status"] == "success":
        print(f"[Watchdog] Successfully posted to Twitter: {result.get('tweet_id')}")
    else:
        print(f"[Watchdog] Error posting to Twitter: {result.get('message')}")


def run_watchdog():
    """Main function to run Watchdog agent"""
    print("Starting Watchdog Agent...")
    print("Scheduled to run daily at 08:00 UTC")
    
    # Schedule daily at 08:00 UTC
    schedule.every().day.at("08:00").do(daily_stats_job)
    
    # For testing, you can also run immediately
    # Uncomment the line below to test
    # daily_stats_job()
    
    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


if __name__ == "__main__":
    run_watchdog()

