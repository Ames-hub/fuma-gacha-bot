import hikari

from cogs.card_group.group import group
from library.database import DB_PATH
import lightbulb
import sqlite3


plugin = lightbulb.Plugin(__name__)

def add_card(name, description, rarity):
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO items (name, description, rarity)
            VALUES (?, ?, ?)
            """,
            (name, description, rarity),
        )
        conn.commit()
        return True
    except sqlite3.OperationalError:
        conn.rollback()
        return False
    finally:
        conn.close()

@group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    name="rarity",
    description="How rare is it?",
    required=True,
    choices=["Common", "Uncommon", "Difficult", "Rare", "Fictional"]
)
@lightbulb.option(
    name="name",
    description="The name of the card",
    required=True,
    type=hikari.OptionType.STRING,
)
@lightbulb.option(
    name="description",
    description="How would you describe the card?",
    required=False,
    default="This card has not been described.",
    type=hikari.OptionType.STRING,
)
@lightbulb.add_cooldown(bucket=lightbulb.buckets.UserBucket, length=120, uses=1)
@lightbulb.add_checks(
    lightbulb.guild_only
)
@lightbulb.command(name='create', description="Create a card that can be in any set of three!")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def bot_command(ctx: lightbulb.SlashContext):
    success = add_card(ctx.options.name, ctx.options.description, ctx.options.rarity)
    if success:
        await ctx.respond(
            embed=(
                hikari.Embed(
                    title="Card Created!",
                    description=f"Your card has successfully been created!",
                )
            )
        )
    else:
        await ctx.respond(
            embed=(
                hikari.Embed(
                    title="Card Created!",
                    description=f"Your card has not been created!",
                    color=0xff0000,
                )
            )
        )

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
