from library import decorators as dc
from library.botapp import botapp
import lightbulb
import hikari
import time

plugin = lightbulb.Plugin(__name__)

@botapp.command()
@lightbulb.app_command_permissions(dm_enabled=True)
@lightbulb.command(name='cd', description="Get a full list of all cooldowns in progress!")
@lightbulb.implements(lightbulb.SlashCommand)
@dc.prechecks('cooldown list')
async def bot_command(ctx: lightbulb.SlashContext):
    embed = (
        hikari.Embed(
            title="<:agathedonut:1454905529016123474> Your Current Cooldowns <:agathedonut:1454905529016123474>",
            description="This is a complete list of the remainder for the cooldown of each command.\n",
            colour=0x0000FF
        )
    )

    all_cooldowns = botapp.d['cooldowns'].get(ctx.author.id, {})
    now = time.time()
    cooldown_txt = ""

    for cmd_id, expiry in all_cooldowns.items():
        wait_time = int(expiry - now)
        if wait_time <= 0:
            continue

        if wait_time <= 120:
            time_unit = "second(s)"
        elif wait_time <= 3599:
            time_unit = "minute(s)"
            wait_time = (wait_time + 59) // 60
        elif wait_time <= 86399:
            time_unit = "hour(s)"
            wait_time = (wait_time + 3599) // 3600
        else:
            time_unit = "day(s)"
            wait_time = (wait_time + 86399) // 86400

        cooldown_txt += (
            f"*__{cmd_id}__*\n"
            f"{int(wait_time)} {time_unit} remaining\n\n"
        )

    if len(cooldown_txt) == 0:
        cooldown_txt = "All cooldowns are over!"

    embed.add_field(
        name="Cooldowns",
        value=cooldown_txt
    )

    await ctx.respond(embed, flags=hikari.MessageFlag.EPHEMERAL)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
