from cogs.staff.logging.group import logging_group
from library.database import eventlogs
from library import decorators as dc
import lightbulb
import hikari

plugin = lightbulb.Plugin(__name__)

@logging_group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    name="channel",
    description="Which channel should I log to?",
    required=True,
    type=hikari.OptionType.CHANNEL,
)
@lightbulb.add_checks(
    lightbulb.guild_only
)
@lightbulb.command(name='set', description="Set where we should log stuff.", pass_options=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
@dc.check_admin_status()
@dc.check_bot_ban()
async def bot_command(ctx: lightbulb.SlashContext, channel:hikari.GuildChannel):
    success = eventlogs.set_channel(int(channel.id))
    if success:
        await ctx.respond(
            embed=hikari.Embed(
                title="Success!",
                description=f"The logging channel has been set to {channel.mention}.",
            )
        )
    else:
        await ctx.respond(
            embed=hikari.Embed(
                title="Error!",
                description="The logging channel could not be set.",
            )
        )

    await eventlogs.log_event(
        "Test Log",
        "This channel has been set for logging events for Fumabot."
    )

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
