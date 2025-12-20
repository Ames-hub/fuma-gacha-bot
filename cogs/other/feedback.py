from cogs.other.views.feedback_view import main_view
from library.botapp import miru_client
from library import decorators as dc
import lightbulb
import hikari

plugin = lightbulb.Plugin(__name__)

@plugin.command
@lightbulb.app_command_permissions(dm_enabled=True)
@lightbulb.command(name='feedback', description='Suggestions, ideas, complaints, let us know!')
@lightbulb.implements(lightbulb.SlashCommand)
@dc.prechecks('feedback')
async def bug_report(ctx: lightbulb.SlashContext):
    view = main_view(int(ctx.author.id))
    embed = view.gen_embed()
    viewmenu = view.init_view()
    await ctx.respond(flags=hikari.MessageFlag.EPHEMERAL, embed=embed, components=viewmenu.build())
    miru_client.start_view(viewmenu)
    await viewmenu.wait()

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
