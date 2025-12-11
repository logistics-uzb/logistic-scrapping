import os
from telethon import TelegramClient
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

SESSION_NAME = "mtproto_session"

# GLOBAL CLIENT
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)


async def start_client():
    """
    Telethon client backend start bo'lganda ishga tushadi.
    Disconnect bo'lsa avtomatik reconnect bo'ladi.
    """
    if not client.is_connected():
        await client.start()
    return client


async def fetch_messages(channel: str, limit: int = 20, offset_id: int = 0):
    """
    Xabarlarni limit + offset asosida olish.
    offset_id = 0 → eng yangi xabardan boshlaydi.
    """
    await start_client()

    messages = []
    async for msg in client.iter_messages(channel, limit=limit, offset_id=offset_id):
        messages.append({
            "id": msg.id,
            "text": msg.text,
            "date": msg.date.isoformat() if msg.date else None,
            "views": msg.views
        })

    return messages
