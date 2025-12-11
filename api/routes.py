from fastapi import APIRouter
import asyncio
from api.mtproto.client import fetch_messages
from config.settings import CHANNEL_LIST
from utils.storage import load_last_ids, save_last_ids

router = APIRouter()

@router.get("/mtproto/channels")
async def mtproto_channels(limit: int = 20):
    """
    Bir nechta kanallarni scraping qilish.
    Kanallar .env (CHANNELS=...) ichidan olinadi.
    """

    real_limit = None if limit == 0 else limit

    tasks = [
        fetch_messages(channel, real_limit)
        for channel in CHANNEL_LIST
    ]

    # asyncio.run() emas!
    results = await asyncio.gather(*tasks)

    response = {}
    for i, channel in enumerate(CHANNEL_LIST):
        response[channel] = {
            "count": len(results[i]),
            "messages": results[i]
        }

    return response


@router.get("/mtproto/new")
async def mtproto_new():
    last_ids = load_last_ids()
    batch_size = 200

    response = {}
    new_last_ids = {}

    for channel in CHANNEL_LIST:
        old_last_id = last_ids.get(channel, 0)

        all_new_messages = []
        offset_id = 0

        while True:
            batch = await fetch_messages(channel, batch_size, offset_id)
            if not batch:
                break

            # Telethon iter_messages reverse bo'ladi → sorted
            for msg in batch:
                if msg["id"] > old_last_id:
                    all_new_messages.append(msg)
                else:
                    break  # eski xabarga yetdik

            # Batchni davom ettirish uchun offset
            if batch[-1]["id"] <= old_last_id:
                break

            offset_id = batch[-1]["id"]

        # Agar yangi xabar bor bo'lsa → oxirgi id ni yangilaymiz
        if all_new_messages:
            new_last_ids[channel] = all_new_messages[0]["id"]
        else:
            new_last_ids[channel] = old_last_id

        response[channel] = {
            "new_count": len(all_new_messages),
            "new_messages": all_new_messages
        }

    save_last_ids(new_last_ids)
    return response


