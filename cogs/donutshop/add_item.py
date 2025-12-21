from library.database import eventlogs, donutshop, verify_filter_string
from cogs.donutshop.group import group
from library import decorators as dc
import lightbulb
import sqlite3
import hikari

plugin = lightbulb.Plugin(__name__)

donutshop_type_crossref = {
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
@dc.prechecks('donutshop_additem')
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
        return

    filter_ok, filter_errors = verify_filter_string(filter_arg)
    if not filter_ok:
        error_text = ""
        for error in filter_errors:
            error_text += f"- {error}\n"

        await ctx.respond(
            embed=(
                hikari.Embed(
                    title="Filter Error",
                    description="We cannot proceed because the following errors occured in your filter.\n"
                                f"{error_text}",
                )
            ),
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    try:
        success = donutshop.add_item(
            name=name,
            amount=amount,
            item_type=donutshop_type_crossref[pack_type],
            price=price,
            filter_arg=filter_arg
        )
    except sqlite3.IntegrityError:
        await ctx.respond(
            embed=hikari.Embed(
                title="That name already exists!",
                description="Please pick another name for the pack name."
            )
        )
        return

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
            event_title="Item Added to DonutShop",
            event_text=f"A {pack_type} {amount} Pack with the name {name} has been added to the shop for {price} {plugin.bot.d['coin_name']['normal']}."
        )
    else:
        await ctx.respond(
            embed=(
                hikari.Embed(
                    title="Error!",
                    description="There was an error adding your item to the shop.",
                )
            ),
            flags=hikari.MessageFlag.EPHEMERAL,
        )

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
