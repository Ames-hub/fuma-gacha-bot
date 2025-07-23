from lightbulb.ext import tasks
import lightbulb
import datetime
import logging
import hikari
import miru
import os

os.makedirs('logs', exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=f'logs/{datetime.datetime.now().strftime("%Y-%m-%d")}.log',
)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "none")
if BOT_TOKEN == "none":
    raise Exception("BOT_TOKEN is not set in environment variables. Please set it.")

botapp = lightbulb.BotApp(token=BOT_TOKEN)
tasks.load(botapp)

@botapp.listen(hikari.ShardReadyEvent)
async def ready(event: hikari.ShardReadyEvent) -> None:
    print(f"Ready, Logged in as {event.my_user.username} (Shard {event.shard.id})")

tasks.load(botapp)
miru_client = miru.Client(botapp)