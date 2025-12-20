from library.dbmodules.notifications import get_notifs_enabled, send_notification
from library.botapp import botapp
from lightbulb.ext import tasks
import lightbulb
import time
import os

plugin = lightbulb.Plugin(__name__)
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"


@tasks.task(s=5, wait_before_execution=not DEBUG, auto_start=True)
async def task() -> None:
    now = time.time()

    cooldowns_root = botapp.d.get("cooldowns", {})

    for user_id, cooldowns in list(cooldowns_root.items()):
        for cmd_id, expiry in list(cooldowns.items()):
            if now >= expiry:
                if get_notifs_enabled(user_id):
                    msg_body = (
                        f'The cooldown for the command "{cmd_id}" is over!\n'
                        "You can run it again whenever you like."
                    )
                    await send_notification(
                        int(user_id),
                        msg_body,
                        title="Cooldown Over!"
                    )

                del cooldowns[cmd_id]

        # Clean up empty user entries
        if not cooldowns:
            del cooldowns_root[user_id]


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
