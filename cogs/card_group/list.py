from library.database import dbcards
from library import decorators as dc
from library.botapp import botapp
import lightbulb
import hikari

plugin = lightbulb.Plugin(__name__)

@botapp.command()
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.command(name='list', description="List All the cards the bot has!")
@lightbulb.implements(lightbulb.SlashCommand)
@dc.prechecks()
async def bot_command(ctx: lightbulb.SlashContext):
    embed = (
        hikari.Embed(
            title="Card List",
            description="Here is a list of all the cards the bot has!",
            colour=0x00FF00
        )
    )

    card_list_text = ""
    all_cards = dbcards.list_all()

    for card in all_cards:
        card_list_text += f"{card['identifier']} - {card['description']}\n\n"

    if len(card_list_text) == 0:
        card_list_text = "No cards found!"

    embed.add_field(
        name="Cards",
        value=card_list_text
    )

    await ctx.respond(embed=embed)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
