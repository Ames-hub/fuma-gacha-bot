import lightbulb

plugin = lightbulb.Plugin(__name__)

# This was added since the one who owns the bot wants it to be 'Pokémon battle' not 'economy battle'
name = "bakery"
desc = "All the bakery commands!"
@plugin.command
@lightbulb.command(name, desc)
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def group(ctx: lightbulb.Context) -> None:
    # This shouldn't be able to be called, but if it is, it'll just respond with a message
    msg = f"Hello, {ctx.author.username}! If you can see this message, that's a bug! Please report it.\n"
    await ctx.respond(msg)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
