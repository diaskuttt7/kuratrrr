import re
import pytesseract
from PIL import Image
from telethon import TelegramClient, events, errors
from sympy import sympify
from sympy.core.sympify import SympifyError
import asyncio
import os

channel_username = 'izatlox1'

# Tesseract yo'lini sozlash (serverda bo'lmasa olib tashlash mumkin)
# pytesseract.pytesseract.tesseract_cmd = r"/usr/bin/tesseract"

accounts = [
    {"session": "account1", "api_id": 20262983, "api_hash": "d233b0bf40f861ce947ec5e95510300e", "message": "1346239969"},
    {"session": "account2", "api_id": 23345424, "api_hash": "093c1d9f5afcbcc0bb2e4eeada7cc47c", "message": "8600492921750358"},
    {"session": "account3", "api_id": 27214718, "api_hash": "30c6c94c68567a650b7cf4ec2ee10e9e", "message": "8600492921750358"},
    {"session": "account4", "api_id": 13195192, "api_hash": "ca944410b25fb1e852d8c9f934759e9d", "message": "8600492921750358"},
    {"session": "account5", "api_id": 27187404, "api_hash": "b5e0ce0579333c3c0ef85f7d6e6d1cfd", "message": "8600492921750358"},
    {"session": "account6", "api_id": 24106437, "api_hash": "fef55023c1c956694948afeb0822040a", "message": "8600492921750358"},
    {"session": "account7", "api_id": 22728247, "api_hash": "88ebe4b74a1d54898c5e5bbafff4860a", "message": "8600492921750358"},
    {"session": "account11", "api_id": 28566120, "api_hash": "7cf1b9616ba2cc76642c7ed9340341ff", "message": "8600492921750358"},
    {"session": "account12", "api_id": 22057723, "api_hash": "af8be812e087e8061b0f8f065ecb9624", "message": "8600492921750358"},
    {"session": "account13", "api_id": 21193912, "api_hash": "0ae43a2d7488d361d07c1fd8ef78937d", "message": "8600492921750358"},
    {"session": "account14", "api_id": 25478196, "api_hash": "9f9616e18fb22b17e4a4ece1903ecdbd", "message": "8600492921750358"},
]

clients = []

def extract_expression(text):
    text = re.sub(r'(?<=\d)\s*[xX]\s*(?=\d)', '*', text)
    pattern = r'[\d\s\+\-\*/\^\(\)]+'
    matches = re.findall(pattern, text)
    if matches:
        for m in matches:
            clean = m.strip()
            if clean.isdigit():
                continue
            if any(op in clean for op in ['+', '-', '*', '/', '^']):
                return clean
    return None

async def handle_event(client):
    @client.on(events.NewMessage(chats=channel_username))
    async def handler(event):
        raw_text = event.raw_text

        if raw_text.strip():
            expr = extract_expression(raw_text)
        else:
            file_path = await event.download_media()
            if file_path:
                try:
                    img = Image.open(file_path)
                    raw_text = pytesseract.image_to_string(img)
                    expr = extract_expression(raw_text)
                finally:
                    os.remove(file_path)
            else:
                expr = None

        if not expr:
            print(f"[{client.session.filename}] ℹ️ Matematik ifoda topilmadi.")
            return

        try:
            result = sympify(expr)
            await client.send_message(
                entity=channel_username,
                message=f"{result}",
                comment_to=event.id
            )
            print(f"[{client.session.filename}] ✅ Izoh yuborildi: {expr} = {result}")
        except SympifyError:
            print(f"[{client.session.filename}] ❌ Noto‘g‘ri ifoda: {expr}")
        except Exception as e:
            print(f"[{client.session.filename}] ⚠️ Xatolik: {e}")

async def check_subscription(client, interval=60):
    """Har interval sekundda kanalga obuna bo‘lishini tekshiradi"""
    while True:
        try:
            participant = await client.get_participant(channel_username, 'me')
            if participant:
                print(f"[{client.session.filename}] ✅ Kanalga obuna bo‘lingan")
        except errors.UserNotParticipantError:
            print(f"[{client.session.filename}] ❌ Kanalga obuna emas")
        except Exception as e:
            print(f"[{client.session.filename}] ⚠️ Xatolik obuna tekshirishda: {e}")
        await asyncio.sleep(interval)

async def start_client(acc):
    client = TelegramClient(acc['session'], acc['api_id'], acc['api_hash'])
    await client.start()
    await handle_event(client)
    # Har 60 soniyada obuna tekshiruvchi task
    asyncio.create_task(check_subscription(client))
    print(f"🔗 {acc['session']} ulandi va obuna tekshirish boshlandi.")
    return client

async def main():
    global clients
    clients = await asyncio.gather(*(start_client(acc) for acc in accounts))
    print("🤖 Hammasi ishga tushdi. Kanal kuzatilyapti...")
    await asyncio.gather(*(client.run_until_disconnected() for client in clients))

if __name__ == "__main__":
    asyncio.run(main())
