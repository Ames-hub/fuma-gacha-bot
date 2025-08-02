from cogs.nicho_market.group import group
from library.database import nichoshop
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
async def bot_command(ctx: lightbulb.SlashContext):
    all_stock = nichoshop.list_stock()

    if len(all_stock) == 0:
        await ctx.respond(
            embed=(
                hikari.Embed(
                    title="Nicho Market",
                    description="There are no cards in the market yet.",
                )
                .add_field(
                    "Nothing here!",
                    "There's nothing sold in the market yet. Why don't you sell something? Make some money?"
                )
            )
        )
        return

    stock_count = len(all_stock)

    pageSize = 50
    pageList = []

    # Use a cache to make it so we aren't constantly reforming the pages
    if plugin.bot.d['nicho_shop']['cache']['last_update'] <= datetime.datetime.now() - datetime.timedelta(seconds=15):
        # Puts the entire thing into a page.
        for item in all_stock:
            item_txt = f"**{item['card_id']}, Sold by <@!{item['seller_id']}>**\n"
            pageList[len(pageList) - 1].append(item_txt)
            if len(pageList[len(pageList) - 1]) == pageSize:
                pageList.append([])
        plugin.bot.d['nicho_shop']['cache']['page_list'] = pageList
    else:
        pageList = plugin.bot.d['nicho_shop']['cache']['page_list']

    page = str(pageList[ctx.options.page - 1])
    if len(page) > 1024:
        page = page[:1000] + "... (trunciated)"

    await ctx.respond(
        embed=(
            hikari.Embed(
                title="Nicho Market",
                description="Buy and sell cards! From users, for users.",
            )
            .add_field(
                name=f"Purchasable Cards ({stock_count})",
                value=page,
            )
        )
    )

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
