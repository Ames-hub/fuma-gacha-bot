from library.database import DB_PATH
from library.botapp import botapp
import lightbulb
import sqlite3
import logging
import hikari

plugin = lightbulb.Plugin(__name__)

def save_to_invent(user_id, item_name):
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT FROM inventories WHERE user_id = ? AND item_name = ?
            """,
            (user_id, item_name)
        )
        data = cursor.fetchone()
        if data is None:
            cursor.execute(
                """
                INSERT INTO inventories (user_id, item_name, amount)
                VALUES (?, ?, 1)
                """,
                (user_id, item_name)
            )
        else:
            cursor.execute(
                """
                UPDATE inventories SET amount = ? WHERE user_id = ? AND item_name = ?
                """
            )
        conn.commit()
    except sqlite3.OperationalError:
        conn.rollback()
    finally:
        conn.close()

def pull_random_card(exception_names=[]):
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        placeholders = ','.join('?' for _ in exception_names) or "''"

        # Build a CASE expression to simulate rarity weighting
        query = f'''
        SELECT name, description, rarity FROM items 
        WHERE name NOT IN ({placeholders})
        ORDER BY
            CASE rarity
                WHEN 'common' THEN ABS(RANDOM()) * 1.0
                WHEN 'uncommon' THEN ABS(RANDOM()) * 1.25
                WHEN 'difficult' THEN ABS(RANDOM()) * 1.67
                WHEN 'Rare' THEN ABS(RANDOM()) * 5.0
                WHEN 'Fictional' THEN ABS(RANDOM()) * 8.0
                ELSE ABS(RANDOM()) * 10.0 -- fallback for unknown rarity
            END
        LIMIT 1
        '''

        cursor.execute(query, exception_names)
        data = cursor.fetchone()
        if not data:
            return False
        else:
            return {
                "name": data[0],
                "description": data[1],
                "rarity": data[2],
            }
    except sqlite3.OperationalError as err:
        logging.error(err)
    finally:
        conn.close()

@botapp.command()
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.add_checks(
    lightbulb.guild_only
)
@lightbulb.command(name='pull', description="Pull a selection of 3 cards!")
@lightbulb.implements(lightbulb.SlashCommand)
async def bot_command(ctx: lightbulb.SlashContext):
    cards = []
    card_names = []
    for i in range(3):
        rcard = pull_random_card(exception_names=card_names)

        cards.append(rcard)
        card_names.append(rcard["name"])

        save_to_invent(
            item_name=rcard["name"],
            user_id=int(ctx.author.id),
        )

    embed = (
        hikari.Embed(
            title=f'✨ Pull Result ✨',
            description=f'<@{ctx.author.id}> Pulled the below cards!',
        )
    )

    for card in cards:
        embed.add_field(
            name=card['name'],
            value=f"{card['description']}\nRarity: {card['rarity']}",
            inline=True,
        )

    await ctx.respond(embed=embed)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
