from library.database import economy, pokemarket
from cogs.pokeshop.group import group
from library import decorators as dc
import lightbulb
import hikari

plugin = lightbulb.Plugin(__name__)

@group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    name="item_id",
    description="The pack ID of the card you wish to buy.",
    required=True,
    type=hikari.OptionType.INTEGER,
)
@lightbulb.add_checks(
    lightbulb.guild_only
)
@lightbulb.command(name='buy', description="Buy a card from the pack shop!")
@lightbulb.implements(lightbulb.SlashSubCommand)
@dc.prechecks('poke buy')
async def bot_command(ctx: lightbulb.SlashContext):
    # Gets the price of the pack
    item_id = ctx.options.item_id

    card_pack = pokemarket.get_item(item_id)
    pack_price = card_pack['price']

    account = economy.account(ctx.author.id)
    cur_bal = account.fumacoins.balance()
    if cur_bal < pack_price:
        await ctx.respond(
            embed=(
                hikari.Embed(
                    title="Insufficient Funds!",
                    description=f"You don't have enough coins to buy this pack.\nYou're short {pack_price - cur_bal} PokeCoins.",
                )
            )
        )
        return

    success = account.fumacoins.modify_balance(pack_price, operator="subtract")
    if not success:
        await ctx.respond(
            embed=(
                hikari.Embed(
                    title="Error!",
                    description="There was an error while subtracting the funds.",
                )
            )
        )
        return

    success = pokemarket.give_random_pack(
        user_id=ctx.author.id,
        item_id=item_id,
    )

    if success:
        await ctx.respond(
            embed=(
                hikari.Embed(
                    title="Success!",
                    description="You bought the new card pack!",
                    color=0x00ff00,
                )
            )
        )
    else:
        await ctx.respond(
            embed=(
                hikari.Embed(
                    title="Error!",
                    description="There was an error while buying the card pack.",
                )
            )
        )

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
