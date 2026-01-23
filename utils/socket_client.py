# utils/socket_client.py
import socketio
from config.settings import SOCKET_URL

sio = socketio.AsyncClient()

async def connect_socket():
    await sio.connect(SOCKET_URL)

async def emit_telegram_message(payload):
    if not sio.connected:
        await connect_socket()
    await sio.emit("telegram:new_message_logistics", payload)
