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
                SELECT item_name, amount FROM inventories WHERE user_id = ?
                """,
                (user_id,)
            )
        else:
            cursor.execute(
                """
                SELECT item_name, amount FROM inventories WHERE user_id = ? AND item_name = ?
                """,
                (user_id, search_for,)
            )
        data = cursor.fetchall()

        inventory = {}
        for row in data:
            inventory[row[0]] = row[1]

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

    inventory = get_inventory(ctx.author.id, search)

    invent_str = f"Your Inventory has {len(inventory)} Items."
    for item_name in inventory:
        invent_str += f"\n*__{item_name}__*\n**Amount** {inventory[item_name]}\n"

    lines = invent_str.split("\n")

    # One chunk every 300 lines
    chunk_size = 300
    chunk_list = ["\n".join(lines[i:i+chunk_size]) for i in range(0, len(lines), chunk_size)]

    if page_number > len(chunk_list):
        page_number = len(chunk_list)

    embed = (
        hikari.Embed(
            title=f"{ctx.author.username}'s Inventory",
            description=chunk_list[page_number],
        )
    )
    if search is not None:
        embed.set_footer("This has been filtered to look for cards with a specific name.")
    if len(chunk_list) > 1:
        embed.set_footer(
            text="Your inventory contains too many items to show on one page, use page option to see more.",
        )

    await ctx.respond(embed=embed)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
