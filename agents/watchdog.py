"""
Agent 3 - Watchdog
Daily statistics and social media posting (Twitter/X and/or LinkedIn)
"""
import os
import schedule
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from utils.shared_state import get_statistics
import tweepy
import requests

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


def post_to_linkedin(message: str) -> dict:
    """
    Posts a message to LinkedIn using API v2.
    
    Note: LinkedIn API requires Partner Program approval and OAuth 2.0 authentication.
    This is more complex than Twitter but reaches the target audience directly.
    
    Args:
        message: Post text (max 3000 characters)
    
    Returns:
        Dictionary with status and post ID
    """
    try:
        # LinkedIn API credentials
        access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
        person_urn = os.getenv("LINKEDIN_PERSON_URN")  # Format: "urn:li:person:xxxxx"
        
        if not access_token or not person_urn:
            return {
                "status": "error",
                "message": "LinkedIn API credentials not configured. LinkedIn API requires Partner Program approval."
            }
        
        # LinkedIn API v2 endpoint for sharing
        url = "https://api.linkedin.com/v2/ugcPosts"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        # LinkedIn post structure
        post_data = {
            "author": person_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": message
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        response = requests.post(url, headers=headers, json=post_data)
        
        if response.status_code == 201:
            post_id = response.headers.get("X-LinkedIn-Id", "unknown")
            return {
                "status": "success",
                "post_id": post_id,
                "message": f"LinkedIn post created successfully: {post_id}"
            }
        else:
            return {
                "status": "error",
                "message": f"LinkedIn API error: {response.status_code} - {response.text}"
            }
    
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error posting to LinkedIn: {str(e)}"
        }


def generate_daily_stats_message(platform: str = "twitter") -> str:
    """
    Generates a daily statistics message for social media.
    
    Args:
        platform: "twitter" or "linkedin"
    
    Returns:
        Message text
    """
    stats = get_statistics()
    
    total_amount = stats["total_amount_unlocked"]
    total_rows = stats["total_rows"]
    
    # Format amount with commas
    amount_str = f"${total_amount:,.0f}" if total_amount >= 1000 else f"${total_amount:.2f}"
    
    if platform == "twitter":
        message = (
            f"Yesterday Second-Chance-ADK helped {total_rows} laid-off workers "
            f"unlock an estimated {amount_str} in benefits they didn't know existed. "
            f"#AgentsForGood #AIForGood"
        )
        # Ensure tweet is within 280 character limit
        if len(message) > 280:
            message = message[:277] + "..."
    else:  # LinkedIn
        message = (
            f"📊 Daily Impact Report\n\n"
            f"Yesterday, Second-Chance Agent helped {total_rows} laid-off workers "
            f"unlock an estimated {amount_str} in benefits they didn't know existed.\n\n"
            f"This includes unemployment insurance, SNAP benefits, ACA subsidies, and "
            f"free re-training vouchers.\n\n"
            f"Built with Google's Agent Development Kit (ADK) to help workers access "
            f"the benefits they qualify for.\n\n"
            f"#AgentsForGood #AIForGood #LayoffSupport #UnemploymentBenefits"
        )
    
    return message


def daily_stats_job():
    """
    Daily job that runs at 08:00 UTC to post statistics to social media.
    Posts to Twitter and/or LinkedIn based on configuration.
    """
    print(f"[Watchdog] Running daily stats job at {datetime.utcnow().isoformat()}")
    
    # Get statistics
    stats = get_statistics()
    print(f"[Watchdog] Total amount unlocked: ${stats['total_amount_unlocked']:,.2f}")
    print(f"[Watchdog] Total cases processed: {stats['total_rows']}")
    
    # Determine which platforms to post to
    post_to_twitter_enabled = os.getenv("POST_TO_TWITTER", "true").lower() == "true"
    post_to_linkedin_enabled = os.getenv("POST_TO_LINKEDIN", "false").lower() == "true"
    
    # Post to Twitter (default, easier to set up)
    if post_to_twitter_enabled:
        tweet_text = generate_daily_stats_message("twitter")
        print(f"[Watchdog] Tweet text: {tweet_text}")
        result = post_to_twitter(tweet_text)
        
        if result["status"] == "success":
            print(f"[Watchdog] ✓ Successfully posted to Twitter: {result.get('tweet_id')}")
        else:
            print(f"[Watchdog] ✗ Error posting to Twitter: {result.get('message')}")
    else:
        print(f"[Watchdog] Twitter posting disabled (set POST_TO_TWITTER=true to enable)")
    
    # Post to LinkedIn (optional, requires Partner Program approval)
    if post_to_linkedin_enabled:
        linkedin_text = generate_daily_stats_message("linkedin")
        print(f"[Watchdog] LinkedIn post text: {linkedin_text[:100]}...")
        result = post_to_linkedin(linkedin_text)
        
        if result["status"] == "success":
            print(f"[Watchdog] ✓ Successfully posted to LinkedIn: {result.get('post_id')}")
        else:
            print(f"[Watchdog] ✗ Error posting to LinkedIn: {result.get('message')}")
    else:
        print(f"[Watchdog] LinkedIn posting disabled (set POST_TO_LINKEDIN=true to enable)")
        print(f"[Watchdog] Note: LinkedIn API requires Partner Program approval")


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

