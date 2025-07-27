from cogs.economy.group import group
from library.database import economy
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
async def bot_command(ctx: lightbulb.SlashContext):
    user_account = economy.account(ctx.author.id)

    pc_coin_bal = user_account.pokecoins.balance()
    nc_coin_bal = user_account.nichocoins.balance()

    if pc_coin_bal == 0 or nc_coin_bal == 0:
        embed_colour = 0xff0000
    else:
        embed_colour = 0x00ff00

    await ctx.respond(
        embed=(
            hikari.Embed(
                title="Balance 🔒",
                description=f"You have {pc_coin_bal} PokeCoins,\nand {nc_coin_bal} NichoCoins.",
                color=embed_colour,
            )
        )
    )

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
