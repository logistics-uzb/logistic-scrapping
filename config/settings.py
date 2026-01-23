import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", 8000))

SOCKET_URL = os.getenv("SOCKET_URL", "http://127.0.0.1:5000")

CHANNELS = os.getenv("CHANNELS", "")
CHANNEL_LIST = [c.strip() for c in CHANNELS.split(",") if c.strip()]