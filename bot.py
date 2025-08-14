from library.database import database
from library.botapp import botapp
import datetime
import uvicorn
import asyncio
import os

# Keep DB Up to date
database.modernize()

# Load all extensions
botapp.load_extensions_from("cogs/card_group")
botapp.load_extensions_from("cogs/nicho_market")
botapp.load_extensions_from("cogs/pokemarket")
botapp.load_extensions_from("cogs/economy")
botapp.load_extensions_from("cogs/staff")
botapp.load_extensions_from("cogs/staff/events")
botapp.load_extensions_from("cogs/staff/limited_events")
botapp.load_extensions_from("cogs/staff/botlogging")
botapp.load_extensions_from("cogs/other")

botapp.d['maintainer'] = 913574723475083274
botapp.d['admin_ids'] = [
    913574723475083274,
    299709812848197644,
    690236383410782301,
    340243618101198858,
    740312826253410355
]
botapp.d['admin_roles'] = [
    1386187466897227890, # Admin role
    1386535298346782761, # Center staff Role
]

DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
botapp.d['DEBUG'] = DEBUG

# Init Cache dicts
botapp.d['inventory_username_cache'] = {}
botapp.d['event_checked_cache'] = {}
botapp.d['limited_event_checked_cache'] = {}

botapp.d['pokestore'] = {
    'user_cache': {}
}

botapp.d['nicho_shop'] = {
    "cache": {
        "page_list": [],
        "last_update": datetime.datetime.now() - datetime.timedelta(seconds=30),
    },
    "open": True
}

botapp.d['config'] = {  # The default config
    "event_channel": {
        "id": None,
    },
    "commands": {}  # TODO: Use this to allow command toggling
}

async def main():
    config = uvicorn.Config(
        "webpanel.webpanel:fastapp",
        host="0.0.0.0" if not DEBUG else "127.0.0.1",
        port=8080,
        loop="asyncio",
        lifespan="on",
        reload=False  # <- important
    )
    server = uvicorn.Server(config)

    await asyncio.gather(
        server.serve(),
        botapp.start()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Ending process.")