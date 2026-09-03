from cogs.wishlist.group import wishlist_group
from library.dbmodules.dbuser import userdb
from library.dbmodules import dbcards
from library import decorators as dc
import lightbulb
import hikari


plugin = lightbulb.Plugin(__name__)

@wishlist_group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    name="card_id",
    description="The name or ID of the card you wish to remove from your wishlist.",
    required=True,
    type=hikari.OptionType.STRING
)
@lightbulb.command(name='remove', description="Remove a card from your wishlist!", pass_options=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
@dc.prechecks('wishlist-remove')
async def bot_command(ctx: lightbulb.SlashContext, card_id:str):
    user = userdb(ctx.user.id)
    success = user.wishlist.remove(card_id)
    card = dbcards.view_card(card_id)

    if not card:
        await ctx.respond(
            hikari.Embed(
                title="Card not found!",
                description="That card does not exist."
            )
        )
        return

    card = card[0]

    if success:
        embed = hikari.Embed(
            title="Removed from Wishlist",
            description=f"{ctx.bot.d['card_tier_names']['numeric'][card['tier']]} {card['rarity']}B card was removed from your wishlist!"
        )
    else:
        embed = hikari.Embed(
            title="Failure!",
            description="Could not remove that card from your wishlist! It may not be on your wishlist."
        )

    await ctx.respond(embed)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
