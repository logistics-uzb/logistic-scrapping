import os
from telethon import TelegramClient , events
from dotenv import load_dotenv
from config.settings import CHANNEL_LIST
from utils.socket_client import emit_telegram_message
print(CHANNEL_LIST, "CHANNEL_LIST")
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

SESSION_NAME = "session/mtproto_session"

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


@client.on(events.NewMessage(chats=CHANNEL_LIST))
async def realtime_handler(event):
    """
    Telegram kanal / chatga yangi xabar kelishi bilan
    real-time ishlaydi (MTProto push).
    """
    print("REAL-TIME EVENT:", event)
    msg = event.message
    chat = await event.get_chat()
    data = {
        "tgMessageId": msg.id,
        "channelName": chat.username or str(chat.id),
        "text": msg.message,
        "date": msg.date.isoformat() if msg.date else None,
        "views": msg.views,
    }
    await emit_telegram_message(data)

    # Hozircha console ga chiqaramiz
    # Keyin DB / Socket / Queue ga yuborish mumkin
    print("REAL-TIME MESSAGE:", data)

