from library.botapp import botapp
import datetime
import hikari
import json
import os

conf_file = "config.json"


def _ensure_config():
    if not os.path.exists(conf_file):
        with open(conf_file, "w") as f:
            json.dump(botapp.d["config"], f, indent=4)

    try:
        with open(conf_file, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        # File exists but is empty or broken
        with open(conf_file, "w") as f:
            json.dump(botapp.d["config"], f, indent=4)
        return botapp.d["config"]


def set_channel(channel_id):
    data = _ensure_config()
    data["event_channel"]["id"] = channel_id

    with open(conf_file, "w") as f:
        json.dump(data, f, indent=4)

    return True


def get_channel():
    data = _ensure_config()
    return data["event_channel"]["id"]


async def log_event(event_title, event_text):
    channel_id = get_channel()
    if not channel_id:
        return False

    embed = (
        hikari.Embed(
            title="Event Log",
            description=f"Event Log of {datetime.datetime.now().strftime('%d/%m/%Y %I:%M %p')}",
            color=0x00FF00,
        )
        .add_field(
            name=event_title,
            value=event_text,
            inline=False,
        )
    )

    try:
        await botapp.rest.create_message(channel_id, embed=embed)
    except hikari.HikariError:
        return False

    return True
