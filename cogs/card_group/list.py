from library.database import dbcards
from library import decorators as dc
from library.botapp import botapp
import lightbulb
import hikari
import math

plugin = lightbulb.Plugin(__name__)

CARDS_PER_PAGE = 10

@botapp.command()
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    "page",
    "Which page of the list do you want to access?",
    type=hikari.OptionType.INTEGER,
    required=True,
)
@lightbulb.command(name="cardlist", description="List all the cards the bot has!")
@lightbulb.implements(lightbulb.SlashCommand)
@dc.prechecks("cardlist")
async def bot_command(ctx: lightbulb.SlashContext):
    page = ctx.options.page

    all_cards = dbcards.list_all()
    total_cards = len(all_cards)

    if total_cards == 0:
        await ctx.respond("No cards found!")
        return

    total_pages = math.ceil(total_cards / CARDS_PER_PAGE)

    # Page bounds check
    if page < 1 or page > total_pages:
        await ctx.respond(
            f"Invalid page number. Please choose a page between **1** and **{total_pages}**."
        )
        return

    start_index = (page - 1) * CARDS_PER_PAGE
    end_index = start_index + CARDS_PER_PAGE
    page_cards = all_cards[start_index:end_index]

    embed = hikari.Embed(
        title="Card List",
        description=f"Showing page **{page}** of **{total_pages}**",
        colour=0x00FF00,
    )

    card_list_text = ""
    for card in page_cards:
        card_list_text += f"**{card['identifier']}**\n{card['description']}\n\n"

    embed.add_field(
        name="Cards",
        value=card_list_text,
        inline=False,
    )

    embed.set_footer(
        text=f"Page {page}/{total_pages} • {total_cards} total cards"
    )

    await ctx.respond(embed=embed)


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
