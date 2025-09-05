from library import decorators as dc
from library.botapp import botapp
import lightbulb
import hikari

plugin = lightbulb.Plugin(__name__)

@botapp.command()
@lightbulb.app_command_permissions(dm_enabled=True)
@lightbulb.command(name='cd', description="Get a full list of all cooldowns in progress!")
@lightbulb.implements(lightbulb.SlashCommand)
@dc.prechecks('cooldown list')
async def bot_command(ctx: lightbulb.SlashContext):
    embed = (
        hikari.Embed(
            title="<:loveball:1389313177392513034> Your Current Cooldowns <:loveball:1389313177392513034>",
            description="This is a complete list of the remainder for the cooldown of each command.\n",
            colour=0x0000FF
        )
    )

    all_cooldowns = botapp.d['cooldowns'].get(ctx.author.id, {})
    cooldown_txt = ""
    for cmd_id, cooldown_s in all_cooldowns.items():
        if cooldown_s <= 0:
            continue
        wait_time = cooldown_s  # cooldown_s is already "seconds remaining"; do not subtract current time
        if wait_time <= 120:  # Under 2 minutes
            time_unit = "second(s)"
            # No change to wait_time (remains in seconds).
        elif wait_time <= 3599:  # Under an hour
            time_unit = "minute(s)"
            wait_time = (wait_time + 59) // 60  # Convert seconds to minutes (rounded up).
        elif wait_time <= 86399:  # Less than a day (under 24 hours)
            time_unit = "hour(s)"
            wait_time = (wait_time + 3599) // 3600  # Convert seconds to hours (rounded up).
        else:  # Greater than or equal to 1 day
            time_unit = "day(s)"
            wait_time = (wait_time + 86399) // 86400  # Convert seconds to days (rounded up).

        if wait_time != 0:
            cooldown_txt += f"*__{cmd_id}__*\n{int(wait_time)} {time_unit} remaining\n\n"
        else:
            cooldown_txt += f"*__{cmd_id}__*\nThis cooldown has ended.\n\n"

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
