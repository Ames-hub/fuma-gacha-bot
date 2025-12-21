from cogs.donutshop.browse_view.change_pack_view import main_view
from cogs.donutshop.group import group
from library.botapp import miru_client
from library import decorators as dc
import lightbulb

plugin = lightbulb.Plugin(__name__)

@group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.add_checks(
    lightbulb.guild_only
)
@lightbulb.command(name='browse', description="Browse the card pack shop!")
@lightbulb.implements(lightbulb.SlashSubCommand)
@dc.prechecks('donutshop browse')
async def bot_command(ctx: lightbulb.SlashContext):
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
