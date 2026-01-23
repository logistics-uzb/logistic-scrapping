import asyncio
from api.mtproto.client import start_client
from loguru import logger
from utils.socket_client import connect_socket


async def init_mtproto():
    logger.info("MTProto client starting...")
    await start_client()
    logger.info("MTProto client started and connected.")
    logger.info("socket client starting...")
    await connect_socket()
    logger.info("socket client started and connected.")