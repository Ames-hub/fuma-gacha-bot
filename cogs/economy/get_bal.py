from cogs.economy.group import group
from library.database import economy
from library import decorators as dc
import lightbulb
import hikari

plugin = lightbulb.Plugin(__name__)

@group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.add_checks(
    lightbulb.guild_only
)
@lightbulb.command(name='bal', description="Check how many coins you have!")
@lightbulb.implements(lightbulb.SlashSubCommand)
@dc.check_bot_ban()
async def bot_command(ctx: lightbulb.SlashContext):
    user_account = economy.account(ctx.author.id)

    fc_coin_bal = user_account.fumacoins.balance()
    nc_coin_bal = user_account.nichocoins.balance()

    if fc_coin_bal == 0 or nc_coin_bal == 0:
        embed_colour = 0xff0000
    else:
        embed_colour = 0x00ff00

    await ctx.respond(
        embed=(
            hikari.Embed(
                title="Balance 🔒",
                description=f"You have {fc_coin_bal} FumaCoins,\nand {nc_coin_bal} NichoCoins.",
                color=embed_colour,
            )
        )
    )

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
