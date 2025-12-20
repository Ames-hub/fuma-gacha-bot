from cogs.staff.group import staff_group
from library import decorators as dc
from library.database import dbcards
import lightbulb
import mimetypes
import hikari

plugin = lightbulb.Plugin(__name__)

@staff_group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    name="group",
    description="The group that the card belongs to.",
    required=False,
    type=hikari.OptionType.STRING
)
@lightbulb.option(
    name="card_era",
    description="The era of the card",
    required=False,
    type=hikari.OptionType.STRING
)
@lightbulb.option(
    name="card_rarity",
    description="The new rarity of what the card is",
    required=False,
    type=hikari.OptionType.STRING,
    choices=["1P", "2P", "3P", "4P", "5P"],
)
@lightbulb.option(
    name="card_tier",
    description="Is this a standard, event or limited card?",
    required=False,
    choices=["Standard", "Event", "Limited"],
    type=hikari.OptionType.STRING,
)
@lightbulb.option(
    name="icon",
    description="Whats the icon for the card?",
    required=False,
    type=hikari.OptionType.ATTACHMENT
)
@lightbulb.option(
    name="description",
    description="The card description",
    required=False
)
@lightbulb.option(
    name="card_id",
    description="The set ID of the card to edit.",
    required=True,
    type=hikari.OptionType.STRING,
)
@lightbulb.add_checks(
    lightbulb.guild_only
)
@lightbulb.command(name='edit', description="Edit an existing card and all its instances (bot admin only)", pass_options=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
@dc.check_admin_status()
@dc.prechecks('edit card')
async def bot_command(ctx: lightbulb.SlashContext, card_id: str, description: str, icon:hikari.Attachment, card_tier:str, card_rarity:str, card_era:str, group:str):
    if not description and not icon and not card_tier and not card_rarity:
        await ctx.respond(
            embed=hikari.Embed(
                title="No options!",
                description="You didn't enter anything to edit!"
            )
        )
        return

    icon_bytes = None
    if icon:
        icon_bytes = await icon.read()
        img_mime, _ = mimetypes.guess_type(icon.filename)

        if not img_mime:
            await ctx.respond(
                embed=hikari.Embed(
                    title="Attachment problem.",
                    description="Could not find the image type?",
                )
            )
            return
        if not img_mime.startswith("image/"):
            await ctx.respond(
                embed=hikari.Embed(
                    title="Attachment problem.",
                    description="Wrong image type. Its preferable to use .png or .jpeg",
                )
            )
            return

    card_tier = plugin.bot.d['card_tier_names']['text'][card_tier]
    card_rarity = int(card_rarity[0])

    success = dbcards.edit_card(
        card_id=card_id,
        description=description,
        icon_bytes=icon_bytes,
        card_tier=card_tier,
        card_rarity=card_rarity,
        card_era=card_era,
        group=group
    )
    
    if success:
        await ctx.respond(
            hikari.Embed(
                title="Success!",
                description="The card has been edited to your specifications.",
                color=0x00FF00
            )
        )
    else:
        await ctx.respond(
            hikari.Embed(
                title="Failure!",
                description="The card has not been edited to your specifications due to an error.",
                color=0x00FF00
            )
        )

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
