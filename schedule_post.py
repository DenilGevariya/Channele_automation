import os
os.environ["TZ"] = "Asia/Kolkata"

import time
import pandas as pd
import schedule
from datetime import datetime
from flask import Flask
from threading import Thread
from post import send_product

app = Flask(__name__)

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

def scheduler_loop():
    load_and_schedule()
    schedule.every(10).seconds.do(load_and_schedule)
    while True:
        schedule.run_pending()
        time.sleep(1)

@app.route("/")
def home():
    return "🚀 Telegram Auto Posting Bot Running"

if __name__ == "__main__":
    Thread(target=scheduler_loop).start()   # Run scheduler in background
    app.run(host="0.0.0.0", port=10000)     # Open a web port for Render
