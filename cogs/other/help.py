from library import decorators as dc
from library.botapp import botapp
import lightbulb
import hikari

plugin = lightbulb.Plugin(__name__)

@botapp.command()
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.command(name='help', description="Get support or information for the bot")
@lightbulb.implements(lightbulb.SlashCommand)
@dc.prechecks('help')
async def bot_command(ctx: lightbulb.SlashContext):
    embed = (
        hikari.Embed(
            title="<:loveball:1389313177392513034> Help and Support <:loveball:1389313177392513034>",
            description="Below, you will find detailed information on Fumabot.\n"
                        "For more help, please visit the server: https://discord.gg/EwnaaNzuQy",
            colour=0x0000FF
        )
        .add_field(
            "Summary",
            "Fumabot is a gacha-kpop mix bot. With Fuma, you can pull cards, add them to your collection or trade cards to get them, "
            "sell them for nicho points (a rare currency) or fuma coins (normal currency), and more!"
        )
        .add_field(
            "Cards",
            "This is a card-pulling gacha bot, so the point is to collect your cards. You can get cards many ways, "
            "Most common are by trading with users, using /pull, using /gymbattle and using /pokebattle.\n"
            "Additionally, You can view what cards you have with /inv (short for inventory)\n\n"
            "Cards also have a rarity level, ranging from 1-5. You'll find this noted by the amount of pokeballs "
            "a card has next to it, higher meaning more rare."
        )
        .add_field(
            "Fuma Economy",
            "This bot features a custom economy. With the two types of coins being, \"Fuma coin\" and \"Nicho Points\"\n"
            "You can earn these by trading, or using /heal, /gymbattle or /pokebattle. Though, these have a long cooldown.\n"
            "Fuma coins are basic coins. Nicho points, however, are rarer and more valuable, and used EXCLUSIVELY for limited cards."
        )
        .add_field(
            "Event/Limited/Standard Cards",
            "A Card can be an event, limited or standard edition. Limted cards are typically only dropped during limited events, "
            "and event cards only at events. While standard cards can be pulled at any time anywhere."
        )
        .add_field(
            "Pokemon battles?",
            "This bot does not feature pokemon battles. Despite the names of those above commands. "
        )
        .add_field(
            "Bugs, Issues and Errors",
            "Have you encountered a bug, issue or error? or even just something you can't figure out?\n"
            "Please tell us about it in the community server!\n"
            "https://discord.gg/EwnaaNzuQy"
        )
    )

    await ctx.respond(embed)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
