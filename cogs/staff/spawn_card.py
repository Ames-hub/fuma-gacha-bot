from library.database import dbcards, eventlogs
from cogs.staff.group import staff_group
from library import decorators as dc
import lightbulb
import hikari


plugin = lightbulb.Plugin(__name__)

@staff_group.child
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
@lightbulb.command(name='gift', description="Spawn a card for someone (bot admin only)", pass_options=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
@dc.check_admin_status()
@dc.prechecks()
async def bot_command(ctx: lightbulb.SlashContext, card_id: str, target_user: hikari.Member, amount: int):
    success = dbcards.spawn_card(card_id=card_id, user_id=int(target_user), amount=amount)
    card = dbcards.view_card(card_id)[0]

    cache_user = ctx.bot.cache.get_member(ctx.guild_id, int(target_user))
    if cache_user is None:
        target_user = await plugin.bot.rest.fetch_member(guild=ctx.guild_id, user=hikari.Snowflake(target_user))
    else:
        target_user = cache_user

    if success:
        await ctx.respond(
            embed=hikari.Embed(
                title=f"{card['identifier']} Spawned!",
                description=f"\"{card['name']}\" has been successfully spawned in {target_user.mention}'s inventory.",
            )
            .set_image(
                hikari.Bytes(
                    dbcards.load_img_bytes(card_id),
                    "image.png",
                )
            )
        )

        await eventlogs.log_event(
            "Card Spawned",
            f"The card {card_id} has been spawned in to {target_user.username}'s inventory."
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
