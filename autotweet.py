import tweepy
import datetime
import os

# Authenticate with secrets (Render will provide them)
client = tweepy.Client(
    consumer_key=os.environ["API_KEY"],
    consumer_secret=os.environ["API_SECRET"],
    access_token=os.environ["ACCESS_TOKEN"],
    access_token_secret=os.environ["ACCESS_SECRET"]
)

def year_progress(year=2025):
    start = datetime.datetime(year, 1, 1)
    end = datetime.datetime(year + 1, 1, 1)
    now = datetime.datetime.utcnow()
    total_seconds = (end - start).total_seconds()
    passed_seconds = (now - start).total_seconds()
    percent = int((passed_seconds / total_seconds) * 100)  # whole number only
    return percent

def post_tweet():
    percent = year_progress()
    text = f"2025 is {percent}% complete..."
    client.create_tweet(text=text)

if _name_ == "_main_":
    post_tweet()