import os
import asyncio
import random
from telethon import TelegramClient , events
from telethon.errors import FloodWaitError
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
_client_lock = asyncio.Lock()


async def start_client():
    """
    Telethon client backend start bo'lganda ishga tushadi.
    Disconnect bo'lsa avtomatik reconnect bo'ladi.
    """
    async with _client_lock:
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


# =============================
# Additional integration for outbound messaging from NestJS
# New executable code appended without modifying existing logic above.
# =============================
from typing import Any, Dict, List

try:
    from loguru import logger  # prefer existing project logger
except Exception:  # pragma: no cover - fallback to print if loguru unavailable
    class _FallbackLogger:
        def info(self, *args, **kwargs):
            print(*args)
        def warning(self, *args, **kwargs):
            print(*args)
        def error(self, *args, **kwargs):
            print(*args)
    logger = _FallbackLogger()


def _normalize_group_identifier(group: str) -> str:
    """
    Normalize a group identifier to a username acceptable by Telethon send_message.
    - Trim whitespace
    - If it looks like a t.me link, extract the slug
    - Ensure it starts with '@' when it's a slug/username
    - If it's a numeric ID or already starts with '@', keep as is (but add '@' for slug without it)
    """
    if not group:
        return group
    g = str(group).strip()

    # Convert t.me links to slug
    if g.startswith("https://t.me/") or g.startswith("http://t.me/") or g.startswith("t.me/"):
        # Split by '/' and take last non-empty segment
        # Remove schema and domain to get the path
        if 't.me/' in g:
            path = g.split('t.me/', 1)[1]
        else:
            path = g
        slug = path.split('/', 1)[0].split('?', 1)[0]
        g = slug

    # If looks like a numeric ID (e.g., -1001234567890), return as is
    if g.startswith('-') and g[1:].isdigit():
        return g
    if g.isdigit():
        return g

    # Ensure leading '@' for usernames/slugs
    if not g.startswith('@'):
        g = '@' + g
    return g


async def send_message_to_groups(message: str, groups: list[str]) -> None:
    """
    Send a text message to multiple Telegram groups/channels using the existing Telethon client.
    - Ensures client is started
    - Normalizes each group identifier to a valid username format
    - Sends messages sequentially with per-group error handling
    """
    # Basic validation
    if not isinstance(message, str) or not message.strip():
        logger.warning("send_message_to_groups: empty or invalid message provided")
        return
    if not groups:
        logger.warning("send_message_to_groups: no groups provided")
        return

    await start_client()

    for raw_group in groups:
        try:
            username = _normalize_group_identifier(raw_group)
            if not username:
                logger.warning(f"Skipping empty group identifier: {raw_group}")
                continue

            await client.send_message(username, message)
            logger.info(f"Message sent to {username}")
            
            # Anti-spam uchun tasodifiy kutish (3-8 soniya)
            delay = random.randint(3, 8)
            logger.info(f"Spam filtridan o'tish uchun kutish: {delay} soniya...")
            await asyncio.sleep(delay)
            
        except FloodWaitError as e:
            logger.error(f"Telegram spam limiti (FloodWait)! {e.seconds} soniya kutish talab etiladi.")
            await asyncio.sleep(e.seconds)
            
        except Exception as exc:
            # Log and continue with next group
            try:
                g_repr = username if 'username' in locals() else str(raw_group)
            except Exception:
                g_repr = str(raw_group)
            logger.error(f"Failed to send message to {g_repr}: {exc}")
            
            # Xatolik bo'lganda ham ozgina kutish tavsiya etiladi
            await asyncio.sleep(2)
            continue


async def handle_nestjs_send(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Entry-point callable by NestJS (via queue/HTTP integration layer) to send messages.
    Expects payload like: {"message": "Text", "groups": ["@group1", "@group2"]}
    Returns a small status dictionary.
    """
    try:
        message = payload.get("message") if isinstance(payload, dict) else None
        groups = payload.get("groups") if isinstance(payload, dict) else None
        if not isinstance(groups, list):
            groups = []

        await send_message_to_groups(message=message, groups=[str(g) for g in groups])
        return {"status": "ok", "sent_to": len(groups)}
    except Exception as exc:
        logger.error(f"handle_nestjs_send error: {exc}")
        return {"status": "error", "error": str(exc)}
