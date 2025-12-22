from library import decorators as dc
from library.botapp import botapp
import lightbulb
import hikari
import time

plugin = lightbulb.Plugin(__name__)

# TODO: Temporary. Migrate to web panel ASAP.
@botapp.command()
@lightbulb.app_command_permissions(dm_enabled=True)
@lightbulb.command(name='cdstatus', description="An admin only command!")
@lightbulb.implements(lightbulb.SlashCommand)
@dc.prechecks('cooldown toggle')
async def bot_command(ctx: lightbulb.SlashContext):
    if int(ctx.author.id) not in [913574723475083274, 340243618101198858, 299709812848197644]:
        await ctx.respond(
            hikari.Embed(
                title="Bad Permissions!",
                description="You are not a bot admin."
            )
        )
        return
    embed = (
        hikari.Embed(
            title="Status Changed!",
            description=f"Cooldowns online: {not botapp.d['cooldowns_on']}"
        )
    )
    botapp.d['cooldowns_on'] = not botapp.d['cooldowns_on']

    await ctx.respond(embed, flags=hikari.MessageFlag.EPHEMERAL)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
