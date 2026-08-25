import json
import os

conf_file = "config.json"

default_config = {  # The default config
    "event_channel": {
        "id": None,
    },
    "BOT_TOKEN": None
}

def ensure_config():
    if not os.path.exists(conf_file):
        with open(conf_file, "w") as f:
            json.dump(default_config, f, indent=4)

    try:
        with open(conf_file, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        # File exists but is empty or broken
        with open(conf_file, "w") as f:
            json.dump(default_config, f, indent=4)
        return default_config

def get_file() -> dict:
    ensure_config()
    with open(conf_file, "r") as f:
        return json.load(f)

def update_file(data:dict):
    ensure_config()
    with open(conf_file, "w") as f:
        return json.dump(data, f, indent=4)