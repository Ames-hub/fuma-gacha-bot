from library.database import DB_PATH, has_admin_role
from cogs.staff.group import group
import lightbulb
import sqlite3
import logging
import hikari

plugin = lightbulb.Plugin(__name__)

def rm_card(card_id):
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            DELETE FROM global_cards WHERE identifier = ?
            """,
            (card_id,),
        )
        conn.commit()
        return True
    except sqlite3.OperationalError as err:
        logging.error(err, exc_info=err)
        conn.rollback()
        return False
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
    name="custom_id",
    description="The custom ID for the card. Defaults to randomness.",
    required=True,
    type=hikari.OptionType.STRING,
)
@lightbulb.add_checks(
    lightbulb.guild_only
)
@lightbulb.command(name='remove_card', description="Create a card that can be in any set of three!")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def bot_command(ctx: lightbulb.SlashContext):
    if has_admin_role(ctx.member.role_ids) is False:
        await ctx.respond(
            embed=hikari.Embed(
                title="Unauthorized",
                description="You are not allowed to use this command!",
            ),
            flags=hikari.MessageFlag.EPHEMERAL
        )
        return

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

    success = rm_card(custom_id)
    if success is True:
        await ctx.respond(
            embed=(
                hikari.Embed(
                    title="Success",
                    description="Your card has been deleted."
                )
            )
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
