from cogs.staff.group import staff_group
import lightbulb

plugin = lightbulb.Plugin(__name__)

name = "limited"
desc = "All event commands"
@staff_group.child
@lightbulb.command(name, desc)
@lightbulb.implements(lightbulb.SlashSubGroup)
async def l_event_group(ctx: lightbulb.Context) -> None:
    # This shouldn't be able to be called, but if it is, it'll just respond with a message
    msg = f"Hello, {ctx.author.username}! If you can see this message, that's a bug! Please report it.\n"
    await ctx.respond(msg)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
