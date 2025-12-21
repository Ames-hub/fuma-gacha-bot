from library.database import eventlogs, donutshop
from cogs.donutshop.group import group
from library import decorators as dc
import lightbulb
import hikari

plugin = lightbulb.Plugin(__name__)

donutshop_type_crossref = {
    "Random Pack": 0,
    "Choice Pack": 1,
}

@group.child
@lightbulb.app_command_permissions(dm_enabled=True)
@lightbulb.option(
    name="name",
    description="What is it named? (its item ID)",
    required=True,
    type=hikari.OptionType.STRING,
)
@lightbulb.command(name='rmitem', description="Remove an item from the pokemarket!", pass_options=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
@dc.check_admin_status()
@dc.prechecks('donutshop rmitem')
async def bot_command(ctx: lightbulb.SlashContext, name):
    success = donutshop.delete_item(name)
    if success:
        await ctx.respond(
            embed=(
                hikari.Embed(
                    title="Item Deleted",
                    description=f"The item `{name}` has been deleted from the market.",
                    color=0x00FF00
                )
            ),
        )
        await eventlogs.log_event(
            "Item Deleted from donutshop",
            f"The item `{name}` has been deleted from the market."
        )
    else:
        await ctx.respond(
            embed=(
                hikari.Embed(
                    title="Error!",
                    description="There was an error while deleting the item.",
                    color=0xFF0000
                )
            ),
        )

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
