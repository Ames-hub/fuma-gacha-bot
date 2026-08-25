from library import settings as config
from library.botapp import botapp
import datetime
import hikari
import json

def set_channel(channel_id):
    data = config.ensure_config()
    data["event_channel"]["id"] = channel_id

    with open(config.conf_file, "w") as f:
        json.dump(data, f, indent=4)

    return True

def get_channel():
    data = config.ensure_config()
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
