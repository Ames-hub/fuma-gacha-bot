from cogs.staff.events.group import event_group
from library.database import dbcards, events
from library import decorators as dc
import lightbulb
import hikari

plugin = lightbulb.Plugin(__name__)

# TODO: Have this command not allow you to assosciate a card to 2 events.

@event_group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    name="card_id",
    description="What's the ID of the card to assosciate with the event?",
    required=True,
    type=hikari.OptionType.STRING,
)
@lightbulb.option(
    name="event_name",
    description="What's the name of the event?",
    required=True,
)
@lightbulb.add_checks(
    lightbulb.guild_only
)
@lightbulb.command(name='assosciate', description="Assosciate a card with an event.", pass_options=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
@dc.check_admin_status()
@dc.check_bot_ban()
async def bot_command(ctx: lightbulb.SlashContext, event_name, card_id):
    # Check card exists
    card_exists = dbcards.check_exists(card_id=card_id)
    if not card_exists:
        await ctx.respond(
            embed=hikari.Embed(
                title="Card Not Found",
                description="The card ID you are trying to assosciate with the event does not exist.",
                color=0xff0000,
            ),
            flags=hikari.MessageFlag.EPHEMERAL
        )
        return
    card_tier = dbcards.get_tier(card_id=card_id)
    if card_tier != "Event":
        if card_tier == "Limited":
            await ctx.respond(
                embed=hikari.Embed(
                    title="Card Tier Incompatibility",
                    description="The card you are trying to assosciate with the standard event is a limited event card.",
                    color=0xff0000,
                ),
                flags=hikari.MessageFlag.EPHEMERAL
            )
            return
        await ctx.respond(
            embed=hikari.Embed(
                title="Card Tier Incompatibility",
                description="The card you are trying to assosciate with the event is not an event card.",
                color=0xff0000,
            ),
            flags=hikari.MessageFlag.EPHEMERAL
        )
        return

    assosciated_cards = events.get_assosciated_cards(event_name=event_name)
    if card_id in assosciated_cards:
        await ctx.respond(
            embed=hikari.Embed(
                title="Card Assosciated",
                description="This card is already assosciated with this event.",
                color=0xff0000,
            ),
            flags=hikari.MessageFlag.EPHEMERAL
        )
        return

    try:
        success = events.assosciate_card(event_name, card_id)
    except events.EventCardAssosciationError:
        await ctx.respond(
            embed=hikari.Embed(
                title="Assosciation Error",
                description="This card is already assosciated with this event.",
                color=0xff0000,
            ),
        )
        return

    if success:
        await ctx.respond(
            embed=hikari.Embed(
                title="Success!",
                description=f"The event card with the ID {card_id} has been assosciated with the event.",
            )
        )
    else:
        await ctx.respond(
            embed=hikari.Embed(
                title="Error!",
                description="The card could not be assosciated with the event.",
            )
        )

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
