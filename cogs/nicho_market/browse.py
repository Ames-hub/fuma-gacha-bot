from cogs.nicho_market.group import group
from library.database import nichoshop
from library import decorators as dc
import lightbulb
import datetime
import hikari

plugin = lightbulb.Plugin(__name__)

@group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    name="hide_too_expensive",
    description="Hide offers that cost too much for you to buy.",
    required=False,
    type=hikari.OptionType.BOOLEAN,
    default=False,
)
@lightbulb.option(
    name="page",
    description="Which page to view?",
    required=False,
    type=hikari.OptionType.INTEGER,
    default=1,
    min_value=1,
)
@lightbulb.add_checks(
    lightbulb.guild_only
)
@lightbulb.command(name='browse', description="Browse the public card market!")
@lightbulb.implements(lightbulb.SlashSubCommand)
@dc.prechecks('nicho browse')
async def bot_command(ctx: lightbulb.SlashContext):
    all_stock = nichoshop.list_stock()

    # Remove unavailable stock
    all_stock = [item for item in all_stock if bool(item['available']) == True]

    stock_count = len(all_stock)

    if stock_count == 0:
        await ctx.respond(
            embed=(
                hikari.Embed(
                    title="Nicho Shop",
                    description="There are no cards in the market yet.",
                    colour=0xff0000,
                )
                .add_field(
                    "Nothing here!",
                    "There's nothing sold in the market yet.\nWhy don't you sell something? Make some money?"
                )
            )
        )
        return

    pageSize = 50
    pageList = {}

    # Use a cache to make it so we aren't constantly reforming the pages
    if plugin.bot.d['nicho_shop']['cache']['last_update'] <= datetime.datetime.now() - datetime.timedelta(seconds=15):
        # Puts the entire thing into a page.
        page_counter = 1
        pageList[1] = []  # Initialise the page list.
        for item in all_stock:
            item_txt = f"*{item['amount']}x {item['card_id']}* for {item['price']} PokeCoins, Sold by {item['seller_disp_name']}\nOffer ID: {item['offer_id']}"
            if len(pageList[page_counter]) == pageSize:
                pageList[page_counter] = []
                page_counter += 1
            pageList[page_counter].append(item_txt)
        plugin.bot.d['nicho_shop']['cache']['page_list'] = pageList
    else:
        pageList = plugin.bot.d['nicho_shop']['cache']['page_list']

    page = pageList[ctx.options.page]
    page_content = "\n".join(page)

    if len(page) > 1024:
        page_content = page[:1000] + "... (trunciated)"

    await ctx.respond(
        embed=(
            hikari.Embed(
                title="Nicho Shop",
                description="Buy and sell cards! From users, for users.",
                colour=0x00ff00,
            )
            .add_field(
                name=f"Purchasable Cards ({stock_count})",
                value=page_content,
            )
        )
    )

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
