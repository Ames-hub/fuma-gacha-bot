from library.database import DB_PATH, has_admin_role
from cogs.staff.group import group
import lightbulb
import mimetypes
import sqlite3
import logging
import random
import hikari

plugin = lightbulb.Plugin(__name__)

def add_card(card_id, name, description, rarity, img_bytes):
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute(
            f"""
            INSERT INTO global_cards (identifier, name, description, rarity, img_bytes)
            VALUES (?, ?, ?, ?, ?)
            {"RETURNING global_cards.identifier" if card_id is None else ""}
            """,
            (card_id, str(name), str(description), int(rarity), img_bytes),
        )
        conn.commit()
        if card_id is None:
            return {'success': True, 'card_id': cur.fetchone()[0]}
        return {'success': True, 'card_id': card_id}
    except sqlite3.OperationalError as err:
        logging.error(err, exc_info=err)
        conn.rollback()
        return {'success': False, 'card_id': None}
    finally:
        conn.close()

rarity_crossref = {
    "common": 1,
    "uncommon": 2,
    "difficult": 3,
    "rare": 4,
    "fictional": 5,
}

@group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    name="rarity",
    description="How rare is it?",
    required=True,
    choices=[item.capitalize() for item in rarity_crossref.keys()],
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
    type=hikari.OptionType.STRING,
)
@lightbulb.add_checks(
    lightbulb.guild_only
)
@lightbulb.command(name='create_card', description="Add a new card to the collection (bot admin only)")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def bot_command(ctx: lightbulb.SlashContext):
    rarity = rarity_crossref[ctx.options.rarity.lower()]
    card_id = ctx.options.custom_id

    if has_admin_role(ctx.member.role_ids) is False:
        await ctx.respond(
            embed=hikari.Embed(
                title="Unauthorized",
                description="You are not allowed to use this command!",
            ),
            flags=hikari.MessageFlag.EPHEMERAL
        )
        return

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

    attachment: hikari.Attachment = ctx.options.icon
    img_mime, _ = mimetypes.guess_type(attachment.filename)
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

    try:
        addresult = add_card(
            card_id=card_id,
            name=name,
            description=ctx.options.description,
            rarity=rarity,
            img_bytes=img_bytes,
        )
    except sqlite3.IntegrityError:
        logging.warning(f"User {ctx.author.id} has attempted to make a card with the pre-existing ID {card_id}.")
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
                            f"Card ID: `id:{card_id}`\n",
            )
        )
        if random.choice([True, False]):
            embed.set_footer(
                text=f"Make use of the ID in searching by prefixing \"ID:(your ID)\"",
            )

        await ctx.respond(
            embed=embed,
        )
    else:
        await ctx.respond(
            embed=(
                hikari.Embed(
                    title="Card Not Created!",
                    description=f"Your card has not been created!",
                    color=0xff0000,
                )
            )
        )

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
