from library.database import DB_PATH
from library.botapp import botapp
import lightbulb
import sqlite3
import hikari

plugin = lightbulb.Plugin(__name__)

def view_card(name):
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT name, description, rarity FROM items WHERE name = ?
            """,
            (name,),
        )
        data = cur.fetchone()
        conn.close()
        if data is None:
            return {}
        else:
            return {
                'name': data[0],
                'description': data[1],
                'rarity': data[2],
            }
    except sqlite3.OperationalError:
        conn.rollback()
        conn.close()
        return False

@botapp.command()
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    name="name",
    description="The name of the card",
    required=True,
    type=hikari.OptionType.STRING,
)
@lightbulb.add_checks(
    lightbulb.guild_only
)
@lightbulb.command(name='view', description="View a card that exists!")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def bot_command(ctx: lightbulb.SlashContext):
    card = view_card(ctx.options.name)

    if type(card) is dict:
        if card.get('name', None) is not None:
            await ctx.respond(
                embed=(
                    hikari.Embed(
                        title="Card Located!",
                    )
                    .add_field(
                        name=card['name'],
                        value=f"{card['description']} - *{card['rarity'].upper()}*",
                    )
                )
            )
        else:
            await ctx.respond(
                embed=(
                    hikari.Embed(
                        title="Card Not Found!",
                        description=f"The card you requested was not found.\nIs the capitalization correct?",
                    )
                )
            )
    else:
        await ctx.respond(
            embed=(
                hikari.Embed(
                    title="There was a problem.",
                    description="Something went wrong, please alert the developers!",
                )
            )
        )

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
