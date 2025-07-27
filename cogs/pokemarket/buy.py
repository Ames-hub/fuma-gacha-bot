from library.database import economy, dbcards
from cogs.pokemarket.group import group
import lightbulb
import hikari

plugin = lightbulb.Plugin(__name__)

@group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    name="pack_id",
    description="The pack ID of the card you wish to buy.",
    required=True,
    type=hikari.OptionType.INTEGER,
)
@lightbulb.add_checks(
    lightbulb.guild_only
)
@lightbulb.command(name='buy', description="Buy a card from the pack market!")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def bot_command(ctx: lightbulb.SlashContext):
    if plugin.bot.d['pokeshop']['open'] is False:
        await ctx.respond(
            embed=(
                hikari.Embed(
                    title="PokeMarket",
                    description="The card pack market is currently closed.",
                )
            )
        )
        return

    # Gets the price of the pack
    card_pack = plugin.bot.d['pokeshop']['stock'][ctx.options.pack_id]
    pack_price = card_pack['price']

    account = economy.account(ctx.author.id)
    cur_bal = account.pokecoins.balance()
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

    success = account.pokecoins.modify_balance(pack_price, operator="subtract")
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

    notice_msg = ""
    for number in [0,1,2]:
        spawn_success = dbcards.spawn_card(
            amount=1,
            card_id=card_pack['pack'][number]['identifier'],
            user_id=ctx.author.id,
        )
        if not spawn_success:
            card_price = (card_pack['pack'][number]['rarity'] * 6) + card_pack['pack'][number]['tier']
            account.pokecoins.modify_balance(card_price, operator="add")
            notice_msg += (f"\n**Card #{number + 1} with ID {card_pack['pack'][number]['identifier']} could not be spawned.\n"
                           f"You've been refunded its full price of {card_price}.**\n")
            continue

    if len(notice_msg) == 0:
        await ctx.respond(
            embed=(
                hikari.Embed(
                    title="Success!",
                    description=f"You've successfully bought a card pack for {pack_price} PokeCoins.",
                )
            )
        )
    else:
        await ctx.respond(
            embed=(
                hikari.Embed(
                    title="Hmm..",
                    description=f"You've bought a card pack for {pack_price} PokeCoins.\n\nHowever, {notice_msg}",
                )
            )
        )

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
