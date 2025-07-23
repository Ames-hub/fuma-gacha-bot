from library.database import dbcards
from library import decorators as dc
from library.botapp import botapp
from io import BytesIO
from PIL import Image
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
@dc.check_bot_ban()
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

        cards.append(rcard)
        card_names.append(rcard["identifier"])
        dbcards.save_to_invent(
            item_identifier=rcard["identifier"],
            item_name=rcard["name"],
            user_id=int(ctx.author.id),
        )
        card_imgs.append(dbcards.load_img_bytes(rcard["identifier"]))  # Assumes returns BytesIO

    # --- Combine images ---
    pil_imgs = [Image.open(img).convert("RGBA") for img in card_imgs]

    gap = 20
    total_width = sum(img.width for img in pil_imgs) + gap * (len(pil_imgs) - 1)
    max_height = max(img.height for img in pil_imgs)

    final_img = Image.new("RGBA", (total_width, max_height), (255, 255, 255, 0))

    x_offset = 0
    for img in pil_imgs:
        final_img.paste(img, (x_offset, 0))
        x_offset += img.width + gap

    img_bytes = BytesIO()
    final_img.save(img_bytes, format="PNG")
    img_bytes.seek(0)

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
        hikari.Bytes(img_bytes.read(), "pull_result.png")
    )

    await ctx.respond(embed=embed)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
