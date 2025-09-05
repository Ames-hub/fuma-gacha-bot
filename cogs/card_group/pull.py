from library.database import dbcards, combine_image, dbuser
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
@lightbulb.add_checks(
    lightbulb.guild_only
)
@lightbulb.command(name='pull', description="Pull a selection of 3 cards!")
@lightbulb.implements(lightbulb.SlashCommand)
@dc.prechecks(cmd_id="pull", cooldown_s=120)
async def bot_command(ctx: lightbulb.SlashContext):
    cards = []
    card_names = []
    card_imgs = []

    if len(dbcards.list_all(pullable_only=True)) != 0:
        await ctx.respond(
            embed=hikari.Embed(
                title="Pulling cards...",
                description="Drumroll please! 🥁🥁🥁",
            )
        )

    for i in range(3):
        rcard = dbcards.pull_random_card(exception_names=card_names)
        if rcard is False:
            await ctx.respond(
                embed=hikari.Embed(
                    title="Not enough cards!",
                    description="You need at least 3 cards for pulls to work!",
                )
            )
            return

        card_id = rcard.get('identifier')

        cards.append(rcard)
        card_names.append(card_id)
        dbcards.save_to_invent(
            item_identifier=card_id,
            item_name=rcard["name"],
            user_id=int(ctx.author.id),
        )
        card_imgs.append(dbcards.load_img_bytes(card_id))  # Assumes returns BytesIO

    image = combine_image(card_imgs)

    embed = hikari.Embed(
        title='✨ Pull Result ✨',
        description=f'<@{ctx.author.id}> Pulled the below cards!',
    )

    for card in cards:
        own_count = dbuser.get_inventory(ctx.author.id, card_id=card['identifier'])[card['identifier']]['amount']
        if own_count != 0:
            own_text = f"You own {own_count} of these"
        else:
            own_text = "✨ *! New Card Unlocked !* ✨"
        embed.add_field(
            name=card['name'],
            value=f"{own_text}\n\n{card['description']}\n{rarity_crossref[card['rarity']]}",
            inline=True,
        )

    embed.set_image(
        image
    )

    await ctx.edit_last_response(embed=embed)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
