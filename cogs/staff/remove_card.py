from library.database import dbcards, eventlogs
from cogs.staff.group import staff_group
from library import decorators as dc
import lightbulb
import hikari


plugin = lightbulb.Plugin(__name__)

rarity_crossref = {
    "common": 1,
    "uncommon": 2,
    "difficult": 3,
    "rare": 4,
    "fictional": 5,
}

@staff_group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    name="custom_id",
    description="The custom ID for the card. Defaults to randomness.",
    required=True,
    type=hikari.OptionType.STRING,
)
@lightbulb.command(name='rmcard', description="Delete a card.")
@lightbulb.implements(lightbulb.SlashSubCommand)
@dc.check_admin_status()
@dc.prechecks('rmcard')
async def bot_command(ctx: lightbulb.SlashContext):
    custom_id = ctx.options.custom_id
    if " " in custom_id:
        await ctx.respond(
            embed=hikari.Embed(
                title="Bad Format",
                description="You cannot have spaces in your card ID!",
            ),
            flags=hikari.MessageFlag.EPHEMERAL
        )
        return

    success = dbcards.rm_card(custom_id)
    if success is True:
        await ctx.respond(
            embed=(
                hikari.Embed(
                    title="Success",
                    description="Your card has been deleted."
                )
            )
        )

        await eventlogs.log_event(
            "Card Deleted",
            f"The card with the ID {custom_id} has been deleted."
        )
    else:
        await ctx.respond(
            embed=(
                hikari.Embed(
                    title="Uh oh!",
                    description=f"Your card has not been deleted!",
                    color=0xff0000,
                )
            )
        )

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
