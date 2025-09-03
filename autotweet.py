from datetime import datetime, timezone, timedelta
from PIL import Image, ImageDraw
import os
import time
import tweepy

# --- Twitter Auth ---
auth = tweepy.OAuth1UserHandler(
    os.environ["API_KEY"],
    os.environ["API_SECRET"],
    os.environ["ACCESS_TOKEN"],
    os.environ["ACCESS_SECRET"]
)
api = tweepy.API(auth)

# --- File to store last posted percent ---
LAST_PERCENT_FILE = "last_percent.txt"

# --- Continuous loop ---
while True:
    now = datetime.now(timezone.utc)
    year = now.year
    start = datetime(year, 1, 1, tzinfo=timezone.utc)
    end = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
    total_seconds = (end - start).total_seconds()
    seconds_per_percent = total_seconds / 100

    # Current integer percent
    percent_float = (now - start).total_seconds() / total_seconds * 100
    percent_int = int(percent_float)

    # Read last posted percent
    if os.path.exists(LAST_PERCENT_FILE):
        with open(LAST_PERCENT_FILE, "r") as f:
            try:
                last_percent = int(f.read())
            except:
                last_percent = None
    else:
        last_percent = None

    # Only post if new percent
    if last_percent != percent_int:
        # --- Determine tweet text ---
        if percent_int == 0:
            tweet_text = f"Welcome to {year}! The year is 0% complete."
        elif percent_int >= 100:
            tweet_text = f"{year} is 100% complete! Thank you all for cooperating and following, and have a wonderful {year + 1}!"
        else:
            tweet_text = f"{percent_int}% of {year} completed"

        # --- Create smooth loading bar image ---
        width, height = 600, 120
        img = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(img)
        bar_x0, bar_y0, bar_x1, bar_y1 = 50, 40, 550, 80
        draw.rectangle([bar_x0, bar_y0, bar_x1, bar_y1], outline="black", width=3)
        bar_width = int((percent_float / 100) * (bar_x1 - bar_x0))
        juice_color = (255, 128, 0)  # bright orange
        if bar_width > 0:
            draw.rectangle([bar_x0, bar_y0, bar_x0 + bar_width, bar_y1], fill=juice_color)
        file_path = "progress.png"
        img.save(file_path)

        # --- Post tweet with image ---
        media = api.media_upload(file_path)
        api.update_status(status=tweet_text, media_ids=[media.media_id])

        # --- Update last posted percent ---
        with open(LAST_PERCENT_FILE, "w") as f:
            f.write(str(percent_int))

        # --- Clean up image ---
        try:
            os.remove(file_path)
        except Exception:
            pass

    # --- Calculate time until next percent increment ---
    next_percent_time = start + timedelta(seconds=(percent_int + 1) * seconds_per_percent)
    sleep_seconds = (next_percent_time - datetime.now(timezone.utc)).total_seconds()
    if sleep_seconds < 0:
        sleep_seconds = 0  # safeguard for leap seconds or slight drift

    # Sleep until next percent increment
    time.sleep(sleep_seconds)