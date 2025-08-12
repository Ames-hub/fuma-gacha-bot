from library.database import dbcards, combine_image
from library import decorators as dc
from library.botapp import botapp
import lightbulb
import hikari

plugin = lightbulb.Plugin(__name__)

@botapp.command()
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.add_checks(
    lightbulb.guild_only
)
@lightbulb.add_cooldown(
    120, 1, lightbulb.buckets.UserBucket
)
@lightbulb.command(name='pull', description="Pull a selection of 3 cards!")
@lightbulb.implements(lightbulb.SlashCommand)
@dc.prechecks()
async def bot_command(ctx: lightbulb.SlashContext):
    cards = []
    card_names = []
    card_imgs = []

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
        embed.add_field(
            name=card['name'],
            value=f"{card['description']}\nRarity: {card['rarity']}",
            inline=True,
        )

    embed.set_image(
        image
    )

    await ctx.respond(embed=embed)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
