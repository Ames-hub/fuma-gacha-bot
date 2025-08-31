from library.database import nichoshop, economy, dbcards
from cogs.nicho_market.group import group
from library import decorators as dc
import lightbulb
import hikari

plugin = lightbulb.Plugin(__name__)

@group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    name="offer_id",
    description="What's the ID of the offer?",
    required=True,
    type=hikari.OptionType.INTEGER,
    min_value=0,
)
@lightbulb.add_checks(
    lightbulb.guild_only
)
@lightbulb.command(name='buy', description="Buy an item offer!", pass_options=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
@dc.prechecks('nicho buy')
async def bot_command(ctx: lightbulb.SlashContext, offer_id):
    try:
        purchase_data = nichoshop.purchase_offer(
            buyer_id=ctx.author.id,
            offer_id=offer_id,
        )
    except nichoshop.OfferNotFoundError:
        await ctx.respond(
            embed=hikari.Embed(
                title="Not found!",
                description="The offer you are trying to purchase does not exist.",
                color=0xFF0000
            )
        )
        return
    except nichoshop.OfferUnavailableError:
        await ctx.respond(
            embed=hikari.Embed(
                title="Unavailable!",
                description="The offer you are trying to purchase is unavailable.",
            )
        )
        return
    except economy.account.InsufficientFundsError:
        await ctx.respond(
            embed=hikari.Embed(
                title="Insufficient funds!",
                description="You don't have enough money to purchase this offer.",
                color=0xFF0000
            )
        )
        return

    if purchase_data is False:
        await ctx.respond(
            embed=hikari.Embed(
                title="Error!",
                description="There was an error while purchasing the card from the market.",
                color=0xFF0000
            )
        )
        return

    success = purchase_data.get('success')

    if success:
        image = dbcards.load_img_bytes(purchase_data['transaction']['given_card_id'])
        price = purchase_data['transaction']['price']
        amount_bought = purchase_data['transaction']['given_amount']
        bought_card_id = purchase_data['transaction']['given_card_id']
        await ctx.respond(
            embed=hikari.Embed(
                title="Success!",
                description="The card has been purchased and added to your inventory!",
                color=0x00FF00
            )
            .add_field(
                name="You accepted this offer!",
                value=f"Card \"{bought_card_id}\", Amount: {amount_bought} for {price} pokecoins",
                inline=True,
            )
            .set_image(hikari.Bytes(image, "cardphoto.png"))
        )
    else:
        await ctx.respond(
            embed=hikari.Embed(
                title="Error!",
                description="There was an error while purchasing the card from the market.",
                color=0xFF0000
            )
        )

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
