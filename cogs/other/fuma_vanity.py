from library import decorators as dc
from library.botapp import botapp
import lightbulb
import hikari

plugin = lightbulb.Plugin(__name__)

@botapp.command()
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.command(name='fumabot', description="Get an invite to the server, or add the bot to your own server!")
@lightbulb.implements(lightbulb.SlashCommand)
@dc.prechecks('vanity')
async def bot_command(ctx: lightbulb.SlashContext):
    embed = (
        hikari.Embed(
            title="<:loveball:1389313177392513034> Thank you for picking Fumabot <:loveball:1389313177392513034>",
            description="Your contribution by using this bot is appreciated.",
            colour=0x00FF00
        )
        .add_field(
            name="Invite the bot",
            value="[Click me to invite the bot to your server!](https://discord.com/oauth2/authorize?client_id=1387493386575020164)"
        )
        .add_field(
            name="Join the community",
            value="[Click me to join in!](https://discord.gg/EwnaaNzuQy)"
        )
        .set_thumbnail(hikari.files.URL(str(botapp.get_me().avatar_url), "fumabot.png"))
        .set_footer(
            "If you're still wondering how to get started, use /help!"
        )
    )

    await ctx.respond(embed)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
