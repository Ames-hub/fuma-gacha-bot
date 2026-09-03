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
    description="The name or ID of the card you wish for!",
    required=True,
    type=hikari.OptionType.STRING
)
@lightbulb.command(name='add', description="Add a card to your wishlist!", pass_options=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
@dc.prechecks('wishlist-add')
async def bot_command(ctx: lightbulb.SlashContext, card_id:str):
    user = userdb(ctx.user.id)
    success = user.wishlist.add(card_id)
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
            title="Added to Wishlist! ✨",
            description=(
                f"{ctx.bot.d['card_tier_names']['numeric'][card['tier']]} {card['rarity']}B card `{card['identifier']}` added to your wishlist!\n"
                f"{ctx.bot.d['rarity_emojis_text'][card['rarity']]}"
            )
        )
        img = hikari.Bytes(card['img_bytes'], "card.png")
        embed.set_image(img)
    else:
        embed = hikari.Embed(
            title="Failure!",
            description="Could not add that card to your wishlist!"
        )

    await ctx.respond(embed)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
