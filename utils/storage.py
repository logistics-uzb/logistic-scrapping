import json
import os

LAST_FILE = "data/last.json"


def load_last_ids():
    if not os.path.exists(LAST_FILE):
        return {}

    with open(LAST_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data.get("channels", {})


def save_last_ids(channel_ids: dict):
    data = {"channels": channel_ids}
    with open(LAST_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
