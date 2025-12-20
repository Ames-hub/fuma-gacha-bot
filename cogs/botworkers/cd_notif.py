from library.dbmodules.notifications import get_notifs_enabled, send_notification
from library.botapp import botapp
from lightbulb.ext import tasks
import lightbulb
import time
import os

plugin = lightbulb.Plugin(__name__)
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

@tasks.task(s=5, wait_before_execution=False if DEBUG else True, auto_start=True)
async def task() -> None:
    for user_id in botapp.d['cooldowns']:
        cooldowns_dict = botapp.d['cooldowns'][user_id]
        for item in cooldowns_dict:
            if cooldowns_dict[item] <= time.time():
                # Cooldown is over
                do_notifs = get_notifs_enabled(user_id)
                if do_notifs:
                    msg_body = f"The cooldown for the command \"{item}\" is over!\nYou can run it when you choose to now."
                    await send_notification(int(user_id), msg_body, title="Cooldown Over!")
                del botapp.d['cooldowns'][user_id][item]

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))