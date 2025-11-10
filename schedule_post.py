import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
from post import send_product
import gspread
from google.oauth2.service_account import Credentials

SHEET_URL = "https://docs.google.com/spreadsheets/d/12Ed5V6MtxAX4YYew7Ba3mAcZyM83DpVyjin8OIcnWEU/edit#gid=0"

creds = Credentials.from_service_account_file(
    "service_account.json",
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)
client = gspread.authorize(creds)
sheet = client.open_by_url(SHEET_URL).sheet1


def clean_time(t):
    for fmt in ("%H:%M", "%I:%M %p", "%H:%M:%S"):
        try:
            return datetime.strptime(str(t).strip(), fmt).strftime("%H:%M")
        except:
            pass
    return str(t).strip()


def run_scheduler():
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    today = now.strftime("%d-%m-%Y")

    df = pd.DataFrame(sheet.get_all_records())

    posts_to_send = []

    for index, row in df.iterrows():
        if str(row.get("posted", "")).strip() == "✅":
            continue

        if str(row["post_date"]).strip() != today:
            continue

        scheduled_time_str = clean_time(row["post_time"])
        scheduled_time = datetime.strptime(f"{today} {scheduled_time_str}", "%d-%m-%Y %H:%M")
        scheduled_time = scheduled_time.replace(tzinfo=ZoneInfo("Asia/Kolkata"))

        diff = (now - scheduled_time).total_seconds() / 60

        if 0 <= diff <= 40:
            posts_to_send.append(index)

    if posts_to_send:
        posted_col = sheet.find("posted").col
        for i in posts_to_send:
            send_product(i)
            sheet.update_cell(i + 2, posted_col, "✅")
        print("✅ Completed batch post.")
    else:
        print(f"No posts scheduled right now ({now.strftime('%H:%M')}).")


if __name__ == "__main__":
    run_scheduler()
