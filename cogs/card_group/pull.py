from cogs.card_group.group import group
import lightbulb

plugin = lightbulb.Plugin(__name__)

@group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.add_checks(
    lightbulb.guild_only
)
@lightbulb.command(name='pull', description="Pull a selection of 3 cards!")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def bot_command(ctx: lightbulb.SlashContext):
    await ctx.respond("This command is currently under development!")

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
