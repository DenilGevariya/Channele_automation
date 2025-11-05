import os
os.environ["TZ"] = "Asia/Kolkata"

import time
import pandas as pd
import schedule
from datetime import datetime
from post import send_product

SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/12Ed5V6MtxAX4YYew7Ba3mAcZyM83DpVyjin8OIcnWEU/export?format=csv&gid=0"

def load_and_schedule():
    schedule.clear()
    df = pd.read_csv(SHEET_CSV_URL)
    today = datetime.now().strftime("%d-%m-%Y")

    for index, row in df.iterrows():
        post_date = str(row["post_date"]).strip()
        post_time = str(row["post_time"]).strip()

        if post_date == today:
            schedule.every().day.at(post_time).do(send_product, index=index)
            print(f"✅ Scheduled: {row['product_name']} at {post_time}")

load_and_schedule()

# refresh schedule every 10 sec
schedule.every(10).seconds.do(load_and_schedule)

print("🚀 Bot is Running on Render 24x7...")

while True:
    schedule.run_pending()
    time.sleep(1)
