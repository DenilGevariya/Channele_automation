import os
os.environ["TZ"] = "Asia/Kolkata"

import pandas as pd
from datetime import datetime
from post import send_product

SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/12Ed5V6MtxAX4YYew7Ba3mAcZyM83DpVyjin8OIcnWEU/export?format=csv&gid=0"

def run_scheduler():
    now_date = datetime.now().strftime("%d-%m-%Y")   # Example: 08-02-2025
    now_time = datetime.now().strftime("%H:%M")      # Example: 14:05

    print(f"⏱ Checking schedule: {now_date} {now_time}")

    df = pd.read_csv(SHEET_CSV_URL)

    for index, row in df.iterrows():
        post_date = str(row["post_date"]).strip()
        post_time = str(row["post_time"]).strip()

        # If sheet time matches current time → Send post
        if post_date == now_date and post_time == now_time:
            print(f"🚀 Sending post: {row['product_name']} at {post_time}")
            send_product(index)
            return  # stop after sending one post for this minute

    print("✅ No scheduled post at this time.")

if __name__ == "__main__":
    run_scheduler()
