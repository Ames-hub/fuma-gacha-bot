from cogs.donutshop.buy_view.buy_choice_pack_view import main_view
from library.database import economy, donutshop
from library.botapp import miru_client
from cogs.donutshop.group import group
from library.dbmodules import dbcards
from library import decorators as dc
import lightbulb
import hikari

plugin = lightbulb.Plugin(__name__)

@group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    name="item_id",
    description="The pack name of the card you wish to buy.",
    required=True,
    type=hikari.OptionType.STRING,
)
@lightbulb.add_checks(
    lightbulb.guild_only
)
@lightbulb.command(name='buy', description="Buy a card from the pack shop!")
@lightbulb.implements(lightbulb.SlashSubCommand)
@dc.prechecks('donutshop buy')
async def bot_command(ctx: lightbulb.SlashContext):
    # Gets the price of the pack
    item_id = ctx.options.item_id

    card_pack = donutshop.get_item(item_id)
    pack_price = card_pack['price']

    account = economy.account(ctx.author.id)
    cur_bal = account.fumacoins.balance()
    if cur_bal < pack_price:
        await ctx.respond(
            embed=(
                hikari.Embed(
                    title="Insufficient Funds!",
                    description=f"You don't have enough coins to buy this pack.\nYou're short {pack_price - cur_bal} {plugin.bot.d['coin_name']['normal']}s.",
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

    if card_pack['type'] == 0:
        pack_give_data = donutshop.give_random_pack(
            user_id=ctx.author.id,
            item_id=item_id,
        )
        success = pack_give_data['success']
        cards_given = pack_give_data['given_cards']

        if success:
            await ctx.respond(
                embed=(
                    hikari.Embed(
                        title="Success!",
                        description="You bought the new card pack! You received the following cards:\n" +
                        "\n".join([f"- `{card}`" for card in cards_given]),
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
    elif card_pack['type'] == 1:
        success = donutshop.give_choice_pack(
            user_id=ctx.author.id,
            item_id=item_id
        )
        if not success:
            await ctx.respond(
                embed=(
                    hikari.Embed(
                        title="Uh oh!",
                        description="For some reason, we couldn't do this! Please file a bug report :("
                    )
                )
            )
            return

        embed = hikari.Embed(
            title="Thank you for your donutshop purchase!",
            description=f"You bought the choice pack {item_id} for {card_pack['price']} {plugin.bot.d['coin_name']['normal']}, "
            "which lets you pick {card_pack['amount']} cards!\n\n"
            "Click the button below to start picking!"
        )

        view = main_view(card_pack['item_id'])
        
        try:
            embed = view.gen_embed()
        except dbcards.ItemNonexistence:
            await ctx.respond(
                embed=(
                    hikari.Embed(
                        title="No cards!",
                        description="There's no cards we can use for this!"
                    )
                )
            )
            return

        viewmenu = view.init_view()
        await ctx.respond(
            embed=embed,
            components=viewmenu.build(),
            flags=hikari.MessageFlag.EPHEMERAL
        )
        miru_client.start_view(viewmenu)
        await viewmenu.wait()
    else:
        raise ValueError("Wrong card pack type!")

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
