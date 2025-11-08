import requests
import pandas as pd
import os
os.environ["TZ"] = "Asia/Kolkata"
# === CONFIG ===
BOT_TOKEN = "8284958888:AAFrNeQ7FRY9tNzyMV5B3npn9DneCDsBOhs"
CHANNEL = "@hirparaonlinehub"
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/12Ed5V6MtxAX4YYew7Ba3mAcZyM83DpVyjin8OIcnWEU/export?format=csv&gid=0"
# === END CONFIG ===


# Convert Google Drive Preview Link → Direct Download Link
def convert_drive_link(url):
    if "drive.google.com" in url and "/d/" in url:
        file_id = url.split("/d/")[1].split("/")[0]
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    return url


def send_product(index):
    df = pd.read_csv(SHEET_CSV_URL)

    product_name = df.loc[index, "product_name"]
    product_price = df.loc[index, "product_price"]
    raw_url = df.loc[index, "image_url"]

    image_url = convert_drive_link(raw_url)

    caption = f"""
*{product_name}*

✅ Ready Stock   Price - {product_price}/-

Connect with Us Directly on WhatsApp:
https://wa.me/+919586346349

Join Our Telegram Channel for Daily Updates:
https://t.me/hirparaonlinehub

Join Our WhatsApp Community for Daily Updates:
https://chat.whatsapp.com/LiUFoJC2iBYBKqWjRHSiBb?mode=ems_wa_t

*Hardik Hirpara* - +91 70162 55268  
*Tushar Hirpara* - +91 79903 75596
    """

    response = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
        data={"chat_id": CHANNEL, "caption": caption, "parse_mode": "Markdown"},
        files={"photo": requests.get(image_url).content}
    )

    print("Sent:", product_name, "| Status:", response.status_code, response.text)


# Test manually
if __name__ == "__main__":
    send_product(0)
