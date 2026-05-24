import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_photo(photo_path):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    with open(photo_path, 'rb') as photo:
        payload = {"chat_id": TELEGRAM_CHAT_ID, "caption": "📸 Aquí tienes el logo para GanoiBot"}
        files = {"photo": photo}
        response = requests.post(url, data=payload, files=files)
        if response.status_code == 200:
            print("Foto enviada con éxito.")
        else:
            print(f"Error: {response.text}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        send_photo(sys.argv[1])
    else:
        print("Proporciona la ruta de la foto.")
