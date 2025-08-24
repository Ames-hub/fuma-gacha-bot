from library.database import dbcards, eventlogs
from cogs.staff.group import staff_group
from library import decorators as dc
import lightbulb
import mimetypes
import datetime
import sqlite3
import logging
import hikari


plugin = lightbulb.Plugin(__name__)

@staff_group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    name="group",
    description="What group is this card in?",
    required=False,
    default=None,
    type=hikari.OptionType.STRING,
)
@lightbulb.option(
    name="rarity",
    description="How rare is it?",
    required=True,
    choices=["1P", "2P", "3P", "4P", "5P"],
)
@lightbulb.option(
    name="icon",
    description="Whats the icon for the card?",
    required=True,
    type=hikari.OptionType.ATTACHMENT
)
@lightbulb.option(
    name="description",
    description="How would you describe the card?",
    required=False,
    default="This card has not been described.",
    type=hikari.OptionType.STRING,
)
@lightbulb.option(
    name="card_tier",
    description="Is this a standard, event or limited card?",
    required=True,
    choices=["Standard", "Event", "Limited"],
    type=hikari.OptionType.STRING,
)
@lightbulb.option(
    name="name",
    description="The name of the card",
    required=True,
    type=hikari.OptionType.STRING,
)
@lightbulb.option(
    name="custom_id",
    description="The custom ID for the card. Defaults to randomness.",
    required=False,
    default=None,
    min_length=3,
    type=hikari.OptionType.STRING,
)
@lightbulb.command(name='mkcard', description="Add a new card to the collection (bot admin only)")
@lightbulb.implements(lightbulb.SlashSubCommand)
@dc.check_admin_status()
@dc.prechecks()
async def bot_command(ctx: lightbulb.SlashContext):
    rarity = int(ctx.options.rarity[0])
    card_id = ctx.options.custom_id

    if card_id is not None:
        if " " in card_id:
            await ctx.respond(
                embed=hikari.Embed(
                    title="Bad Format",
                    description="You cannot have spaces in your card ID!",
                ),
                flags=hikari.MessageFlag.EPHEMERAL
            )
            return

    card_group = ctx.options.group
    if card_group is None:
        card_group = datetime.datetime.now().strftime("%Y")  # Gets the year.
    elif " " in card_group:
        await ctx.respond(
            embed=hikari.Embed(
                title="Bad Format",
                description="You cannot have spaces in your card group!",
            ),
            flags=hikari.MessageFlag.EPHEMERAL
        )
        return

    attachment: hikari.Attachment = ctx.options.icon
    img_mime, _ = mimetypes.guess_type(attachment.filename)
    if not img_mime:
        await ctx.respond(
            embed=hikari.Embed(
                title="Attachment problem.",
                description="Could not find the image type?",
            )
        )
        return
    if not img_mime.startswith("image/"):
        await ctx.respond(
            embed=hikari.Embed(
                title="Attachment problem.",
                description="Wrong image type.",
            )
        )
        return

    # Converts to bytes
    img_bytes = await attachment.read()
    name = ctx.options.name
    card_tier = ctx.options.card_tier

    card_tier_crossref = {
        "Standard": 1,
        "Event": 2,
        "Limited": 3,
    }

    card_tier = card_tier_crossref[card_tier]

    try:
        addresult = dbcards.add_card(
            card_id=card_id,
            name=name,
            description=ctx.options.description,
            rarity=rarity,
            card_tier=card_tier,
            img_bytes=img_bytes,
            pullable=True if card_tier == 1 else False,
            card_group=card_group,
        )
    except sqlite3.IntegrityError as err:
        logging.warning(f"User {ctx.author.id} has attempted to make a card with the pre-existing ID {card_id}. Err: {err}")
        await ctx.respond(
            embed=hikari.Embed(
                title="Duplicacy Warning",
                description=f"The card ID {card_id} already exists.",
            )
        )
        return

    if addresult['success'] == True:
        if addresult['card_id'] is not None:
            card_id = addresult['card_id']

        embed = (
            hikari.Embed(
                title="Card Created!",
                description="Your card has successfully been created!\n"
                            f"Card ID: `{card_id}`\n",
            )
        )

        await ctx.respond(
            embed=embed,
        )

        await eventlogs.log_event(
            "Card Created",
            f"The card {name} has been created with the ID {card_id}."
        )
    else:
        await ctx.respond(
            embed=(
                hikari.Embed(
                    title="Card Not Created!",
                    description=f"Reason: {addresult['error']}",
                    color=0xff0000,
                )
            )
        )

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
