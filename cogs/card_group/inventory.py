from library.database import DB_PATH
from library.botapp import botapp
import lightbulb
import sqlite3
import logging
import hikari

plugin = lightbulb.Plugin(__name__)

def get_inventory(user_id, search_for=None):
    conn = sqlite3.connect(DB_PATH)

    try:
        cursor = conn.cursor()
        if search_for is None:
            cursor.execute(
                """
                SELECT item_name, item_identifier, amount FROM inventories WHERE user_id = ?
                """,
                (user_id,)
            )
        else:
            search_is_id = " " not in search_for and search_for.lower().startswith("id:")
            if search_is_id:
                search_for = search_for.replace("id:", "")

            cursor.execute(
                f"""
                SELECT item_name, item_identifier, amount
                FROM inventories
                WHERE user_id = ?
                AND {"item_name" if not search_is_id else "item_identifier"} = ?
                """,
                (user_id, search_for,)
            )
        data = cursor.fetchall()

        inventory = {}
        for row in data:
            inventory[row[1]] = {
                "name": row[0],
                "identifier": row[1],
                "amount": row[2],
            }

        return inventory
    except sqlite3.OperationalError as err:
        conn.rollback()
        logging.error(f"An error occurred while running a command: {err}", exc_info=err)
    finally:
        conn.close()

@botapp.command()
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    name="query",
    description="Search your inventory by card name.",
    required=False,
    type=hikari.OptionType.STRING,
    default=None
)
@lightbulb.option(
    name="user",
    description="Check a particular persons inventory.",
    required=False,
    type=hikari.OptionType.MENTIONABLE,
    default=None
)
@lightbulb.option(
    name="page",
    description="Enter which page of your inventory you want!",
    required=False,
    type=hikari.OptionType.INTEGER,
    min_value=1,
    default=1
)
@lightbulb.add_checks(
    lightbulb.guild_only
)
@lightbulb.command(name='inv', description="See your current inventory!")
@lightbulb.implements(lightbulb.SlashCommand)
async def bot_command(ctx: lightbulb.SlashContext):
    search = ctx.options.query
    page_number = int(ctx.options.page) - 1  # index at 0.
    target_user: hikari.Member = ctx.options.user

    inventory = get_inventory(ctx.author.id if target_user is None else int(target_user), search)

    invent_str = f"Your Inventory has {len(inventory)} Items."
    for item_identifier in inventory:
        invent_str += f"\n*__{inventory[item_identifier]['name']}__* - {item_identifier}\n**Amount** {inventory[item_identifier]['amount']}\n"

    lines = invent_str.split("\n")

    # One chunk every 300 lines
    chunk_size = 300
    chunk_list = ["\n".join(lines[i:i+chunk_size]) for i in range(0, len(lines), chunk_size)]

    if page_number > len(chunk_list):
        page_number = len(chunk_list)

    if target_user is not None:
        if botapp.d['inventory_username_cache'].get(target_user) is None:
            target_user = await botapp.rest.fetch_member(ctx.guild_id, target_user)
            target_username = target_user.username
        else:
            target_username = botapp.d['inventory_username_cache'].get(target_user.id)
    else:
        target_username = ctx.author.username

    embed = (
        hikari.Embed(
            title=f"{target_username}'s Inventory",
            description=chunk_list[page_number],
        )
    )

    footer_text = ""
    if search is not None:
        footer_text += f"Search filtered with query: {search}\n"
    if len(chunk_list) > 1:
        footer_text += "Your inventory contains too many items to show on one page, use page option to see more."

    if footer_text != "":
        embed.set_footer(text=footer_text)

    await ctx.respond(embed=embed)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
