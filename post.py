import requests
import pandas as pd

BOT_TOKEN = "8284958888:AAFrNeQ7FRY9tNzyMV5B3npn9DneCDsBOhs"   # replace with your bot token
CHANNEL = "@producttestupdates"   # replace with your channel username

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

    # If only one image → use sendPhoto (more reliable)
    if len(image_links) == 1:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
            data={"chat_id": CHANNEL, "caption": caption, "parse_mode": "Markdown"},
            files={"photo": requests.get(image_links[0]).content}
        )
        print("✅ Sent (single image):", product_name)
        return

    # Otherwise → sendMediaGroup
    files = {}
    media = []

    for i, url in enumerate(image_links):
        img = requests.get(url).content
        file_name = f"image{i}.jpg"
        files[file_name] = (file_name, img, "image/jpeg")
        media.append({
            "type": "photo",
            "media": f"attach://{file_name}",
            "caption": caption if i == 0 else "",
            "parse_mode": "Markdown"
        })

    files_for_request = [(name, data) for name, data in files.items()]

    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMediaGroup",
        data={"chat_id": CHANNEL, "media": json.dumps(media)},
        files=files_for_request
    )

    print("✅ Sent (multi image):", product_name)
