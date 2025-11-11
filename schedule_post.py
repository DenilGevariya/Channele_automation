import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
from post import send_product
import gspread
from google.oauth2.service_account import Credentials
import json
import os

# ================= GOOGLE SHEET CONFIG =================
SHEET_URL = "https://docs.google.com/spreadsheets/d/12Ed5V6MtxAX4YYew7Ba3mAcZyM83DpVyjin8OIcnWEU/edit#gid=0"
# =======================================================

# ✅ Load service account from GitHub Secret (SERVICE_ACCOUNT_JSON)
creds_json = json.loads(os.environ["SERVICE_ACCOUNT_JSON"])
creds = Credentials.from_service_account_info(
    creds_json,
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)
client = gspread.authorize(creds)
sheet = client.open_by_url(SHEET_URL).sheet1


def clean_time(t):
    t = str(t).strip()
    for fmt in ("%H:%M", "%H:%M:%S", "%I:%M %p", "%I:%M%p"):
        try:
            return datetime.strptime(t, fmt).strftime("%H:%M")
        except:
            pass
    # Fix "9:00" → "09:00"
    parts = t.split(":")
    if len(parts) == 2:
        return f"{parts[0].zfill(2)}:{parts[1].zfill(2)}"
    return t


def run_scheduler():
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    today = now.strftime("%d-%m-%Y")

    df = pd.DataFrame(sheet.get_all_records())

    posts_to_send = []

    for index, row in df.iterrows():
        # Skip already posted
        if str(row.get("posted", "")).strip() == "✅":
            continue

        # Skip if date does not match today
        if str(row["post_date"]).strip() != today:
            continue

        # Convert sheet time to 24-hour format
        scheduled_time_str = clean_time(row["post_time"])
        scheduled_time = datetime.strptime(f"{today} {scheduled_time_str}", "%d-%m-%Y %H:%M")
        scheduled_time = scheduled_time.replace(tzinfo=ZoneInfo("Asia/Kolkata"))

        # Calculate time difference
        diff = (now - scheduled_time).total_seconds() / 60

        # ✅ Only send AFTER scheduled time, up to 40 min late
        if 0 <= diff <= 40:
            posts_to_send.append(index)

    # ✅ Send all posts that match
    if posts_to_send:
        posted_col = sheet.find("posted").col
        for i in posts_to_send:
            print(f"🚀 Sending: {df.loc[i, 'product_name']}")
            send_product(i)
            sheet.update_cell(i + 2, posted_col, "✅")

        print("✅ Batch complete.")
    else:
        print(f"⏱ {now.strftime('%H:%M')} - No posts scheduled now.")


if __name__ == "__main__":
    run_scheduler()
