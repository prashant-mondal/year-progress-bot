from datetime import datetime, timezone, timedelta
from PIL import Image, ImageDraw
import os
import time
import tweepy
import git

# --- Twitter Auth ---
auth = tweepy.OAuth1UserHandler(
    os.environ["API_KEY"],
    os.environ["API_SECRET"],
    os.environ["ACCESS_TOKEN"],
    os.environ["ACCESS_SECRET"]
)
api = tweepy.API(auth)

# --- Git repo for last_percent tracking ---
repo = git.Repo(os.getcwd())
LAST_PERCENT_FILE = "last_percent.txt"

def read_last_percent():
    if os.path.exists(LAST_PERCENT_FILE):
        with open(LAST_PERCENT_FILE, "r") as f:
            try:
                return int(f.read())
            except:
                return None
    else:
        return None

def update_last_percent(percent_int):
    with open(LAST_PERCENT_FILE, "w") as f:
        f.write(str(percent_int))
    repo.index.add([LAST_PERCENT_FILE])
    repo.index.commit(f"Update last_percent to {percent_int}")
    origin = repo.remote(name='origin')
    origin.push()

# --- Function to post a percent ---
def post_percent(percent_int, year):
    # Determine tweet text
    if percent_int == 0:
        tweet_text = f"Welcome to {year}! The year is 0% complete."
    elif percent_int >= 100:
        tweet_text = f"{year} is 100% complete! Thank you all for cooperating and following, and have a wonderful {year + 1}!"
    else:
        tweet_text = f"{percent_int}% of {year} completed"

    # Create smooth loading bar image
    width, height = 600, 120
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    bar_x0, bar_y0, bar_x1, bar_y1 = 50, 40, 550, 80
    draw.rectangle([bar_x0, bar_y0, bar_x1, bar_y1], outline="black", width=3)
    bar_width = int((percent_int / 100) * (bar_x1 - bar_x0))
    juice_color = (255, 128, 0)
    if bar_width > 0:
        draw.rectangle([bar_x0, bar_y0, bar_x0 + bar_width, bar_y1], fill=juice_color)
    file_path = "progress.png"
    img.save(file_path)

    # Post tweet
    media = api.media_upload(file_path)
    api.update_status(status=tweet_text, media_ids=[media.media_id])

    # Update last percent on GitHub
    update_last_percent(percent_int)

    # Clean up image
    try:
        os.remove(file_path)
    except Exception:
        pass

# --- Continuous loop ---
while True:
    now = datetime.now(timezone.utc)
    year = now.year
    start = datetime(year, 1, 1, tzinfo=timezone.utc)
    end = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
    total_seconds = (end - start).total_seconds()
    seconds_per_percent = total_seconds / 100

    percent_float = (now - start).total_seconds() / total_seconds * 100
    percent_int = int(percent_float)

    # --- Read last percent ---
    last_percent = read_last_percent()

    # --- Safe mid-year start ---
    if last_percent is None:
        last_percent = percent_int
        update_last_percent(last_percent)

    # --- Catch-up missed percents ---
    missed_percents = []
    if last_percent < percent_int:
        for p in range(last_percent + 1, percent_int + 1):
            missed_percents.append(p)

    for p in missed_percents:
        post_percent(p, year)

    # --- Wait until next integer percent ---
    next_percent_time = start + timedelta(seconds=(percent_int + 1) * seconds_per_percent)
    sleep_seconds = (next_percent_time - datetime.now(timezone.utc)).total_seconds()
    if sleep_seconds < 0:
        sleep_seconds = 0  # safeguard for drift

    time.sleep(sleep_seconds)