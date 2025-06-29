from library.database import DB_PATH
from library.botapp import botapp
import lightbulb
import sqlite3
import hikari

plugin = lightbulb.Plugin(__name__)

rarity_crossref = {
    1: "common",
    2: "uncommon",
    3: "difficult",
    4: "rare",
    5: "fictional",
}

def gift_card(cardname: str, giving_amount: int, giver_id: int, receiver_id: int):
    if giving_amount < 1:
        return "Amount must be at least 1."

    is_id = " " not in cardname and cardname.lower().startswith("id:")
    if is_id:
        cardname = cardname.replace("id:", "")

    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()

        # Step 1: Fetch item from giver
        cur.execute(f"""
            SELECT item_identifier, item_name, amount FROM inventories
            WHERE user_id = ? AND {'item_identifier' if is_id else 'item_name'} = ?
        """, (giver_id, cardname))

        item = cur.fetchone()
        if not item:
            return "Giver doesn't own the item."

        item_identifier, item_name, giver_amount = item

        if giver_amount < giving_amount:
            return f"Not enough quantity to give. You have {giver_amount}."

        # Step 2: Deduct from giver
        if giver_amount == giving_amount:
            cur.execute("""
                DELETE FROM inventories
                WHERE user_id = ? AND item_identifier = ?
            """, (giver_id, item_identifier))
        else:
            cur.execute("""
                UPDATE inventories
                SET amount = amount - ?
                WHERE user_id = ? AND item_identifier = ?
            """, (giving_amount, giver_id, item_identifier))

        # Step 3: Add to receiver
        cur.execute("""
            SELECT amount FROM inventories
            WHERE user_id = ? AND item_identifier = ?
        """, (receiver_id, item_identifier))

        receiver_item = cur.fetchone()
        if receiver_item:
            cur.execute("""
                UPDATE inventories
                SET amount = amount + ?
                WHERE user_id = ? AND item_identifier = ?
            """, (giving_amount, receiver_id, item_identifier))
        else:
            cur.execute("""
                INSERT INTO inventories (item_identifier, item_name, user_id, amount)
                VALUES (?, ?, ?, ?)
            """, (item_identifier, item_name, receiver_id, giving_amount))

        conn.commit()
        return "Transfer successful."

    except sqlite3.OperationalError as e:
        conn.rollback()
        return f"Database error: {e}"
    finally:
        conn.close()


@botapp.command()
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    name="name_or_id",
    description="The name or ID of the card. If using ID, prefix 'id:'",
    required=True,
    type=hikari.OptionType.STRING,
)
@lightbulb.option(
    name="target",
    description="The person to send it to.",
    required=True,
    type=hikari.OptionType.MENTIONABLE,
)
@lightbulb.option(
    name="amount",
    description="How many to send.",
    required=True,
    type=hikari.OptionType.INTEGER,
    min_value=1,
)
@lightbulb.add_checks(
    lightbulb.guild_only
)
@lightbulb.command(name='gift', description="Gift someone a card!", pass_options=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def bot_command(ctx: lightbulb.SlashContext, name_or_id:str, target:hikari.Member, amount:int):
    success = gift_card(
        cardname=str(name_or_id),
        giver_id=int(ctx.author.id),
        receiver_id=int(target),
        giving_amount=int(amount),
    )
    await ctx.respond(success)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
