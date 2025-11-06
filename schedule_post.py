import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
from post import send_product
import gspread
from google.oauth2.service_account import Credentials

SHEET_URL = "https://docs.google.com/spreadsheets/d/12Ed5V6MtxAX4YYew7Ba3mAcZyM83DpVyjin8OIcnWEU/edit#gid=0"

# Google Sheets Auth
creds = Credentials.from_service_account_file(
    "service_account.json",
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)
client = gspread.authorize(creds)
sheet = client.open_by_url(SHEET_URL).sheet1


def clean_time(t):
    try:
        return datetime.strptime(str(t).strip(), "%H:%M").strftime("%H:%M")
    except:
        try:
            return datetime.strptime(str(t).strip(), "%I:%M %p").strftime("%H:%M")
        except:
            try:
                return datetime.strptime(str(t).strip(), "%H:%M:%S").strftime("%H:%M")
            except:
                return str(t).strip()


def run_scheduler():
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    now_date = now.strftime("%d-%m-%Y")

    data = sheet.get_all_records()

    for index, row in enumerate(data):
        post_date = str(row["post_date"]).strip()
        post_time = clean_time(row["post_time"])
        posted = str(row.get("posted", "")).strip()

        # Skip already posted rows
        if posted == "✅":
            continue

        # Skip if date does not match
        if post_date != now_date:
            continue

        # Convert scheduled time to datetime with timezone
        scheduled_time = datetime.strptime(
            f"{post_date} {post_time}", "%d-%m-%Y %H:%M"
        ).replace(tzinfo=ZoneInfo("Asia/Kolkata"))

        # Calculate minute difference
        diff = abs((now - scheduled_time).total_seconds()) / 60

        # ✅ Allowed posting window = 40 minutes
        if diff <= 40:
            print(f"🚀 Posting: {row['product_name']} (Scheduled {post_time}, Now {now.strftime('%H:%M')})")
            send_product(index)

            # ✅ Mark posted in sheet
            posted_col = sheet.find("posted").col
            sheet.update_cell(index + 2, posted_col, "✅")
            print("✅ Marked as posted in sheet")
            return

    print(f"⏱ Checked at {now.strftime('%H:%M')} — No post needed this minute.")


if __name__ == "__main__":
    run_scheduler()
