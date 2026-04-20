from fastapi import APIRouter, Header, HTTPException, status
import asyncio
import os
from typing import List, Optional

from pydantic import BaseModel, Field

from api.mtproto.client import fetch_messages, send_message_to_groups
from config.settings import CHANNEL_LIST
from utils.storage import load_last_ids, save_last_ids

# ✅ Router yaratamiz (faqat shu!)
router = APIRouter()


@router.get("/mtproto/channels")
async def mtproto_channels(limit: int = 20):

    real_limit = None if limit == 0 else limit

    tasks = [
        fetch_messages(channel, real_limit)
        for channel in CHANNEL_LIST
    ]

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

            for msg in batch:
                if msg["id"] > old_last_id:
                    all_new_messages.append(msg)
                else:
                    break

            if batch[-1]["id"] <= old_last_id:
                break

            offset_id = batch[-1]["id"]

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


class SendRequest(BaseModel):
    message: str = Field(..., min_length=1)
    groups: List[str] = Field(default_factory=list)



@router.post("/mtproto/send")
async def mtproto_send(
    payload: SendRequest,
    x_internal_token: Optional[str] = Header(default=None, alias="X-Internal-Token"),
):

    print("SEND ENDPOINT CALLED")

    expected = os.getenv("INTERNAL_API_TOKEN")

    if expected:
        if not x_internal_token or x_internal_token != expected:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized",
            )

    await send_message_to_groups(
        message=payload.message,
        groups=payload.groups
    )

    return {
        "success": True,
        "groupsCount": len(payload.groups),
    }
