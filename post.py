import requests
import pandas as pd
import os
os.environ["TZ"] = "Asia/Kolkata"

BOT_TOKEN = "8284958888:AAFrNeQ7FRY9tNzyMV5B3npn9DneCDsBOhs"  # replace yours
CHANNELS = [
    "@producttestupdates"
]  # Add more channels like "@mychannel2"

SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/12Ed5V6MtxAX4YYew7Ba3mAcZyM83DpVyjin8OIcnWEU/export?format=csv&gid=0"


def convert_drive_link(url):
    if "drive.google.com" in url and "/d/" in url:
        file_id = url.split("/d/")[1].split("/")[0]
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    return url


def send_product(index):
    df = pd.read_csv(SHEET_CSV_URL)

    product_name = df.loc[index, "product_name"]
    product_price = df.loc[index, "product_price"]

    image_links = []
    for col in ["image_1", "image_2", "image_3"]:
        if col in df.columns and str(df.loc[index, col]).strip():
            image_links.append(convert_drive_link(df.loc[index, col]))

    caption = f"""
*{product_name}*

✅ Ready Stock  Price - {product_price}/-

Connect with Us Directly on WhatsApp:
https://wa.me/+919586346349

Join Our Telegram Channel:
https://t.me/+t8ZbFaGZV8M4NTN

Join Our WhatsApp Community:
https://chat.whatsapp.com/LiUFoJC2iBYBKqWjRHSiBb?mode=ems_wa_t

*Hardik Hirpara* - +91 70162 55268  
*Tushar Hirpara* - +91 79903 75596
""".strip()

    for CH in CHANNELS:
        files = []
        media = []

        for i, url in enumerate(image_links):
            img_data = requests.get(url).content
            files.append(("media", (f"image{i}.jpg", img_data, "image/jpeg")))
            media.append({
                "type": "photo",
                "media": f"attach://image{i}.jpg",
                "caption": caption if i == 0 else "",
                "parse_mode": "Markdown"
            })

        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMediaGroup",
            data={"chat_id": CH, "media": str(media).replace("'", '"')},
            files=files
        )

    print(f"✅ Sent: {product_name}")
