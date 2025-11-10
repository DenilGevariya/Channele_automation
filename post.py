import requests
import pandas as pd
import json

# ================= CONFIG =================
BOT_TOKEN = "8284958888:AAFrNeQ7FRY9tNzyMV5B3npn9DneCDsBOhs"   # <-- PUT YOUR BOT TOKEN
CHANNEL = "@HirparaOnlineHub"  # <-- PUT YOUR CHANNEL USERNAME
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/12Ed5V6MtxAX4YYew7Ba3mAcZyM83DpVyjin8OIcnWEU/export?format=csv&gid=0"
# ==========================================


def convert_drive_link(url):
    """Convert Google Drive preview link to direct download."""
    url = str(url).strip()
    if "drive.google.com" in url and "/d/" in url:
        file_id = url.split("/d/")[1].split("/")[0]
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    return url


def send_product(index):
    df = pd.read_csv(SHEET_CSV_URL)

    product_name = df.loc[index, "product_name"]
    product_price = df.loc[index, "product_price"]

    # Collect image links safely (skip empty or NaN)
    image_links = []
    for col in ["image_1", "image_2", "image_3"]:
        if col in df.columns:
            val = str(df.loc[index, col]).strip()
            if val and val.lower() != "nan":
                image_links.append(convert_drive_link(val))

    # Caption Text
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

    # ✅ CASE 1: No images → Send text only
    if len(image_links) == 0:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHANNEL, "text": caption, "parse_mode": "Markdown"}
        )
        print(f"✅ Sent (text only): {product_name}")
        return

    # ✅ CASE 2: One image → sendPhoto
    if len(image_links) == 1:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
            data={"chat_id": CHANNEL, "caption": caption, "parse_mode": "Markdown"},
            files={"photo": requests.get(image_links[0]).content}
        )
        print(f"✅ Sent (1 image): {product_name}")
        return

    # ✅ CASE 3: Multi-images → sendMediaGroup
    files = {}
    media = []

    for i, url in enumerate(image_links):
        img_data = requests.get(url).content
        fname = f"image{i}.jpg"
        files[fname] = (fname, img_data, "image/jpeg")
        media.append({
            "type": "photo",
            "media": f"attach://{fname}",
            "caption": caption if i == 0 else "",
            "parse_mode": "Markdown"
        })

    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMediaGroup",
        data={"chat_id": CHANNEL, "media": json.dumps(media)},
        files=[(name, data) for name, data in files.items()]
    )

    print(f"✅ Sent ({len(image_links)} images): {product_name}")
