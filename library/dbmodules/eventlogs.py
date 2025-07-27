from library.botapp import botapp
import datetime
import hikari
import json

def set_channel(channel_id):
    data = {
        "event_channel": {
            "id": channel_id,
        }
    }
    with open('library/config.json', 'w') as f:
        json.dump(data, f, indent=4)

    return True

def get_channel():
    with open('library/config.json', 'r') as f:
        data = json.load(f)
        return data["event_channel"]["id"]

async def log_event(event_title, event_text):
    embed = (
        hikari.Embed(
            title="Event Log",
            description=f"Event Log of {datetime.datetime.now().strftime('%d/%m/%Y %I:%M %p')}",
            color=0x00FF00,
        )
        .add_field(
            name=event_title,
            value=event_text,
            inline=False
        )
    )

    await botapp.rest.create_message(
        get_channel(),
        embed=embed,
    )
    return True