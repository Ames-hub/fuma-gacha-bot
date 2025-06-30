from library.database import view_card, load_img_bytes
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
    name="name_or_id",
    description="The name or ID of the card. If using ID, prefix 'id:'",
    required=True,
    type=hikari.OptionType.STRING,
)
@lightbulb.add_checks(
    lightbulb.guild_only
)
@lightbulb.command(name='pokedex', description="View a card!")
@lightbulb.implements(lightbulb.SlashCommand)
async def bot_command(ctx: lightbulb.SlashContext):
    card = view_card(ctx.options.name_or_id)

    if type(card) is list:
        if len(card) == 1:
            image_bytes = load_img_bytes(card[0].get('identifier'))
            card = card[0]

            await ctx.respond(
                embed=(
                    hikari.Embed(
                        title="Card Located!",
                    )
                    .add_field(
                        name=card['name'],
                        value=f"{card['description']}\n*{rarity_crossref[card['rarity']]}*",
                    )
                    .set_image(hikari.Bytes(image_bytes, "cardphoto.png"))
                ),
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
