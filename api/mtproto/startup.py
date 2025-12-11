import asyncio
from api.mtproto.client import start_client
from loguru import logger

async def init_mtproto():
    logger.info("MTProto client starting...")
    await start_client()
    logger.info("MTProto client started and connected.")
