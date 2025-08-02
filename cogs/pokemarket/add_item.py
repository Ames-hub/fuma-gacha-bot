from library.database import eventlogs, pokemarket
from cogs.pokemarket.group import group
from library import decorators as dc
import lightbulb
import hikari

plugin = lightbulb.Plugin(__name__)

pokeshop_type_crossref = {
    "Random Pack": 0,
    "Choice Pack": 1,
}

@group.child
@lightbulb.app_command_permissions(dm_enabled=True)
@lightbulb.option(
    name="filter_arg",
    description="How should we filter the items? Enter HELP here for more info!",
    required=True,
    type=hikari.OptionType.STRING,
)
@lightbulb.option(
    name="pack_type",
    description="What type of card pack is this?",
    choices=[
        'Random Pack',
        'Choice Pack',
    ],
    required=True,
    type=hikari.OptionType.STRING,
)
@lightbulb.option(
    name="amount",
    description="How many cards should there be in this pack?",
    required=True,
    type=hikari.OptionType.INTEGER,
    min_value=1,
    max_value=100,
)
@lightbulb.option(
    name="price",
    description="What's the price of this item?",
    required=True,
    type=hikari.OptionType.INTEGER,
    min_value=1,
)
@lightbulb.option(
    name="name",
    description="What should it be named?",
    required=True,
    type=hikari.OptionType.STRING,
)
@lightbulb.command(name='additem', description="Add an item to the market to be purchased!", pass_options=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
@dc.check_admin_status()
@dc.check_bot_ban()
async def bot_command(ctx: lightbulb.SlashContext, name, price, amount, pack_type, filter_arg):
    if filter_arg.lower() == "help":
        await ctx.respond(
            embed=(
                hikari.Embed(
                    title="Filter Help",
                    description="Please visit [This Note](https://gist.github.com/Ames-hub/095e6715a9c1d3adecd22dc0f869bed6) To learn more."
                )
            )
        )

    success = pokemarket.add_item(
        name=name,
        amount=amount,
        item_type=pokeshop_type_crossref[pack_type],
        price=price,
    )

    if success:
        await ctx.respond(
            embed=(
                hikari.Embed(
                    title="Success!",
                    description="Your item has been added to the market!",
                )
            ),
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        await eventlogs.log_event(
            event_title="Item Added to PokeShop",
            event_text=f"A {pack_type} {amount} Pack with the name {name} has been added to the market for {price} PokeCoins."
        )
    else:
        await ctx.respond(
            embed=(
                hikari.Embed(
                    title="Error!",
                    description="There was an error adding your item to the market.",
                )
            ),
            flags=hikari.MessageFlag.EPHEMERAL,
        )

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
