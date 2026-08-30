from library.database import dbcards, combine_image, dbuser
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
@lightbulb.command(name='pull', description="Pull a selection of 3 cards!")
@lightbulb.implements(lightbulb.SlashCommand)
@dc.prechecks(cmd_id="pull", cooldown_s=120)
async def bot_command(ctx: lightbulb.SlashContext):
    cards = []
    card_names = []
    card_imgs = []

    if len(dbcards.list_all(pullable_only=True, include_customs=False)) != 0:
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
        card_imgs.append(dbcards.load_img_bytes(card_id))  # Assumes returns BytesIO

    image = combine_image(card_imgs)

    embed = hikari.Embed(
        title='✨ Pull Result ✨',
        description=f'<@{ctx.author.id}> Pulled the below cards!',
        colour=ctx.bot.d['branding']['embed']
    )

    for card in cards:
        inv_entry = dbuser.get_inventory(ctx.author.id, card_id=card['identifier'])
        if inv_entry:
            own_count = inv_entry[card['identifier']]['amount'] + 1  # Plus one for we're about to get another. This is never just 1.
        else:
            own_count = 1

        if own_count > 1:
            own_text = f"You own {own_count} of these"
        else:
            own_text = "✨ *! New Card Unlocked !* ✨"
        embed.add_field(
            name=f"{card['name']} - `{card['identifier']}`",
            value=f"{own_text}\n\n{card['description']}\n{plugin.bot.d['rarity_emojis_text'][card['rarity']]}",
            inline=True,
        )
        dbcards.save_to_invent(
            item_identifier=card['identifier'],
            item_name=card["name"],
            user_id=int(ctx.author.id), 
        )

    embed.set_image(
        image
    )

    await ctx.edit_last_response(embed=embed)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
