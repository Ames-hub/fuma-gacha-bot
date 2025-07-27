from cogs.pokemarket.browse_view.change_pack_view import main_view
from cogs.pokemarket.group import group
from library.botapp import miru_client
import lightbulb
import hikari

plugin = lightbulb.Plugin(__name__)

@group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.add_checks(
    lightbulb.guild_only
)
@lightbulb.command(name='browse', description="Browse the card pack market!")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def bot_command(ctx: lightbulb.SlashContext):
    if plugin.bot.d['pokeshop']['open'] is False:
        await ctx.respond(
            embed=(
                hikari.Embed(
                    title="PokeMarket",
                    description="The card pack market is currently closed.",
                )
            )
        )
        return

    view = main_view()
    embed = view.gen_embed(ctx.author.id)
    viewmenu = view.init_view()
    await ctx.respond(embed=embed, components=viewmenu.build())
    miru_client.start_view(viewmenu)
    await viewmenu.wait()

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
