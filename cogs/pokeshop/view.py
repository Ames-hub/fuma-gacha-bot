from cogs.pokeshop.group import group
import lightbulb
import hikari

plugin = lightbulb.Plugin(__name__)

@group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.add_checks(
    lightbulb.guild_only
)
@lightbulb.command(name='view', description="View the card market!")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def bot_command(ctx: lightbulb.SlashContext):
    await ctx.respond(
        embed=(
            hikari.Embed(
                title="Fuma Market",
                description="View the card market!",
            )
            .add_field(
                "WIP",
                "This is currently a work in progress, pending development."
                "\nThank you for your patience!"
            )
        )
    )

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
