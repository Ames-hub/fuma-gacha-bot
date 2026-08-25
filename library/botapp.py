from lightbulb.ext import tasks
import lightbulb
import datetime
import logging
import hikari
import dotenv
import miru
import os

os.makedirs('logs', exist_ok=True)

dotenv.load_dotenv(".env")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=f'logs/{datetime.datetime.now().strftime("%Y-%m-%d")}.log',
)

def ensure_bot_token():
    from library import settings  # Its here & in a func to prevent circular import
    BOT_TOKEN = os.environ.get("BOT_TOKEN", None) or settings.get_file()['BOT_TOKEN']
    if BOT_TOKEN is None:
        BOT_TOKEN = input("Enter bot token >>> ")
        if not BOT_TOKEN:
            raise Exception("BOT_TOKEN is not set in environment variables or settings. Please set it.")
        else:
            data = settings.get_file()
            data["BOT_TOKEN"] = BOT_TOKEN
            settings.update_file(data)
    return BOT_TOKEN

botapp = lightbulb.BotApp(token=ensure_bot_token())
tasks.load(botapp)

botapp.d['DB_PATH'] = "botapp.sqlite"

@botapp.listen(hikari.ShardReadyEvent)
async def ready(event: hikari.ShardReadyEvent) -> None:
    print(f"Ready, Logged in as {event.my_user.username} (Shard {event.shard.id})")

tasks.load(botapp)
miru_client = miru.Client(botapp)