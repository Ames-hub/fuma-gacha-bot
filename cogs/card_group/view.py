from library.database import dbcards
from library import decorators as dc
from library.botapp import botapp
import lightbulb
import hikari

plugin = lightbulb.Plugin(__name__)

rarity_crossref = {
    1: "<:loveball:1389313177392513034>",
    2: "<:loveball:1389313177392513034>" * 2,
    3: "<:loveball:1389313177392513034>" * 3,
    4: "<:loveball:1389313177392513034>" * 4,
    5: "<:loveball:1389313177392513034>" * 5,
}

@botapp.command()
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    name="id",
    description="The ID of the card.",
    required=True,
    type=hikari.OptionType.STRING,
)
@lightbulb.add_checks(
    lightbulb.guild_only
)
@lightbulb.command(name='view', description="View a card!")
@lightbulb.implements(lightbulb.SlashCommand)
@dc.prechecks()
async def bot_command(ctx: lightbulb.SlashContext):
    card = dbcards.view_card(ctx.options.id)

    if type(card) is list:
        if len(card) == 1:
            image_bytes = dbcards.load_img_bytes(card[0].get('identifier'))
            card = card[0]

            card_tier_crossref = {
                1: "Standard",
                2: "Event",
                3: "Limited",
            }

            embed = (
                hikari.Embed(
                    title="Card Located!",
                )
                .add_field(
                    name=f"{card['name']} - {card['identifier']}",
                    value=f"{card['description']}\n\n"
                          f"*ID: {card['identifier']}*\n"
                          f"Group: {card['group']}"
                )
                .add_field(
                    name="Rarity",
                    value=f"*{rarity_crossref[card['rarity']]}*",
                )
                .set_image(hikari.Bytes(image_bytes, "cardphoto.png"))
            )
            if card['tier'] != 1:
                embed.add_field(
                    name="Special Type ✨",
                    value=f"{card_tier_crossref[card['tier']]} Card",
                    inline=True
                )
            if card['pullable'] is False:
                embed.add_field(
                    name="Unobtainable",
                    value="This card cannot be pulled randomly.",
                    inline=True,
                )

            await ctx.respond(
                embed
            )
        elif len(card) == 0:
            await ctx.respond(
                embed=(
                    hikari.Embed(
                        title="Card Not Found!",
                        description=f"The card you requested was not found.\nIs the capitalization correct?",
                    )
                )
            )
        elif len(card) > 1:
            embed = (
                hikari.Embed(
                    title="Too many Found!",
                    description=f"We found {len(card) - 1} card(s) more than what's ideal.\nPlease run this command using one of these IDs below instead.",
                )
            )

            cards_text = ""
            for item in card:
                # noinspection PyTypeChecker
                cards_text += f"{item['description']}\nName: {item['name']} | ID: {item['identifier']}\n\n"

            embed.add_field(
                name="Cards",
                value=cards_text
            )

            await ctx.respond(
                embed=embed
            )
    else:
        await ctx.respond(
            embed=(
                hikari.Embed(
                    title="There was a problem.",
                    description="Something went wrong, please alert the developers!",
                )
            )
        )

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
