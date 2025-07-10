from library.database import DB_PATH, has_admin_role
from cogs.staff.group import group
import lightbulb
import sqlite3
import hikari

plugin = lightbulb.Plugin(__name__)

def spawn_card(card_id: str, amount: int, user_id: int):
    if amount < 1:
        return "Amount must be at least 1."

    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()

        card_id = card_id.replace("id:", "")

        # Step 1: Get the item details from global_cards
        cur.execute(f"""
            SELECT identifier, name FROM global_cards
            WHERE identifier = ? AND card_tier IS NOT 3
        """, (card_id,))

        card_data = cur.fetchone()

        if not card_data:
            return False

        item_identifier, item_name = card_data

        # Step 2: Check if the user already has it
        cur.execute("""
            SELECT amount FROM inventories
            WHERE user_id = ? AND item_identifier = ?
        """, (user_id, item_identifier))

        existing = cur.fetchone()
        if existing:
            cur.execute("""
                UPDATE inventories
                SET amount = amount + ?
                WHERE user_id = ? AND item_identifier = ?
            """, (amount, user_id, item_identifier))
        else:
            cur.execute("""
                INSERT INTO inventories (item_identifier, item_name, user_id, amount)
                VALUES (?, ?, ?, ?)
            """, (item_identifier, item_name, user_id, amount))

        conn.commit()
        return "Card spawned successfully."

    except sqlite3.OperationalError as e:
        conn.rollback()
        return f"Database error: {e}"
    finally:
        conn.close()

@group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    name="card_id",
    description="The Custom ID of the card.",
    required=True,
    type=hikari.OptionType.STRING,
)
@lightbulb.option(
    name="target_user",
    description="The user who you wish to give the item to.",
    required=True,
    type=hikari.OptionType.MENTIONABLE,
)
@lightbulb.option(
    name="amount",
    description="The amount of items to give to the user.",
    required=True,
    type=hikari.OptionType.INTEGER,
    min_value=1,
)
@lightbulb.add_checks(
    lightbulb.guild_only
)
@lightbulb.command(name='gift', description="Spawn in a card for someone (bot admin only)", pass_options=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def bot_command(ctx: lightbulb.SlashContext, card_id: str, target_user: hikari.Member, amount: int):
    if has_admin_role(ctx.member.role_ids) is False:
        await ctx.respond(
            embed=hikari.Embed(
                title="Unauthorized",
                description="You are not allowed to use this command!",
            ),
            flags=hikari.MessageFlag.EPHEMERAL
        )
        return

    success = spawn_card(card_id=card_id, user_id=int(target_user), amount=amount)
    if success:
        await ctx.respond(
            embed=hikari.Embed(
                title="Success!",
                description="The card has been successfully spawned in to their inventory.",
            )
        )
    else:
        await ctx.respond(
            embed=hikari.Embed(
                title="Error!",
                description="The card could not be spawned.",
            )
        )

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
