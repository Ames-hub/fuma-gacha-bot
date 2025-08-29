from library.dbmodules.dbuser import invent_errs
from library.database import nichoshop, dbcards
from cogs.nicho_market.group import group
from library import decorators as dc
import lightbulb
import hikari

plugin = lightbulb.Plugin(__name__)

@group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    name="price",
    description="How much are you selling it for?",
    required=True,
    type=hikari.OptionType.INTEGER,
    min_value=0,
    max_value=1500  # TODO: Make this controllable by admins.
)
@lightbulb.option(
    name="amount",
    description="How many are you selling?",
    required=True,
    type=hikari.OptionType.INTEGER,
    min_value=1,
)
@lightbulb.option(
    name="card_id",
    description="What item are you selling by ID? (you need to have it)",
    required=True,
    type=hikari.OptionType.STRING,
)
@lightbulb.add_checks(
    lightbulb.guild_only
)
@lightbulb.command(name='sell', description="Sell an item on the public card market!", pass_options=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
@dc.prechecks('nicho sell')
async def bot_command(ctx: lightbulb.SlashContext, card_id, amount, price):
    exists = dbcards.check_exists(card_id=card_id)
    if not exists:
        await ctx.respond(
            embed=hikari.Embed(
                title="Card Not Found",
                description="The card ID you are trying to sell does not exist.",
                color=0xFF0000
            )
        )
        return

    try:
        offer_id = nichoshop.add_offer(
            card_id=card_id,
            amount=amount,
            price=price,
            seller_id=ctx.author.id,
            seller_disp_name=ctx.author.display_name
        )
    except invent_errs.TooFewItemsError as err:
        await ctx.respond(
            embed=hikari.Embed(
                title="Not enough cards!",
                description=str(err),
                color=0xFF0000
            )
        )
        return
    except invent_errs.InventoryItemNotFound:
        await ctx.respond(
            embed=hikari.Embed(
                title="No such cards!",
                description="You tried to sell a card that you don't own!",
                color=0xFF0000
            )
        )
        return

    if type(offer_id) is int:
        await ctx.respond(
            embed=hikari.Embed(
                title="Success!",
                description="The card has been aded to the trading market to be bought.",
                color=0x00FF00
            )
            .add_field(
                name="Offer ID",
                value=f"The offer ID used for others to purchase the offer is: **{offer_id}**",
                inline=True,
            )
        )
    else:
        await ctx.respond(
            embed=hikari.Embed(
                title="Error!",
                description="There was an error while adding the card to the market.",
                color=0xFF0000
            )
        )

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
