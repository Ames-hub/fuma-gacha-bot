from lightbulb.ext import tasks
import lightbulb
import datetime
import logging
import miru
import os

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
miru_client = miru.Client(botapp)