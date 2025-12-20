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
@dc.prechecks('view card')
async def bot_command(ctx: lightbulb.SlashContext):
    card = dbcards.view_card(ctx.options.id)[0]
    if not card:
        await ctx.respond(
            embed=(
                hikari.Embed(
                    title="Card Not Found!",
                    description=f"The card you requested was not found.\nIs the capitalization correct?",
                )
            )
        )
        return

    try:
        image_bytes = dbcards.load_img_bytes(card.get('identifier'))
    except ValueError:
        await ctx.respond(
            hikari.Embed(
                title="Card Error!",
                description="This card doesn't seem to have an assosciated image, so we can't load it!"
            )
        )
        return

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
                    f"Idol member: {card['idol']}\n"
                    f"Group: {card['group']} - Era: {card['era']}"
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
    if card['is_custom'] is True:
        embed.add_field(
            name="Custom Card",
            value="This card is extremely rare, and extremely special. One of a kind, and made for one being.",
        )

    await ctx.respond(
        embed
    )

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
