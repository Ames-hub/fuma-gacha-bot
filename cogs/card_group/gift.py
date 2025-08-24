from library import decorators as dc
from library.database import dbcards
from library.botapp import botapp
import lightbulb
import hikari

from library.dbmodules.dbcards import gift_errors

plugin = lightbulb.Plugin(__name__)

@botapp.command()
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    name="card_id",
    description="The ID of the card to gift.",
    required=True,
    type=hikari.OptionType.STRING,
)
@lightbulb.option(
    name="target",
    description="The person to send it to.",
    required=True,
    type=hikari.OptionType.MENTIONABLE,
)
@lightbulb.option(
    name="amount",
    description="How many to send.",
    required=True,
    type=hikari.OptionType.INTEGER,
    min_value=1,
)
@lightbulb.add_checks(
    lightbulb.guild_only
)
@lightbulb.command(name='gift', description="Gift someone a card!", pass_options=True)
@lightbulb.implements(lightbulb.SlashCommand)
@dc.prechecks()
async def bot_command(ctx: lightbulb.SlashContext, card_id:str, target:hikari.Member, amount:int):
    if target.id == ctx.author.id:
        await ctx.respond(
            embed=hikari.Embed(
                title="Self-gifting",
                description="You cannot gift yourself a card!",
                color=0xFF0000
            )
        )
        return
    elif target.id == botapp.get_me().id:
        await ctx.respond(
            embed=hikari.Embed(
                title="Invalid Target",
                description="While I appreciate the sentiment, you can't gift me a card ^^'",
                color=0xFF0000
            )
        )
        return

    try:
        success = dbcards.gift_card(
            cardname=str(card_id),
            giver_id=int(ctx.author.id),
            receiver_id=int(target),
            giving_amount=int(amount),
        )
    except gift_errors.BadAmount as err:
        await ctx.respond(
            embed=hikari.Embed(
                title="Bad Amount",
                description=str(err),
                color=0xFF0000
            )
        )
        return
    except gift_errors.NotEnoughOfItem as err:
        await ctx.respond(
            embed=hikari.Embed(
                title="Not Enough Cards",
                description=str(err),
                color=0xFF0000
            )
        )
        return
    except gift_errors.GiverDoesNotOwnCard as err:
        await ctx.respond(
            embed=hikari.Embed(
                title="Not Owned",
                description=str(err),
            )
        )
        return
    except gift_errors.GiftDBError as err:
        await ctx.respond(
            embed=hikari.Embed(
                title="Error",
                description=str(err),
                color=0xFF0000
            )
        )
        return


    if success:
        card = dbcards.view_card(card_id)[0]
        image = dbcards.load_img_bytes(card['identifier'])
        await ctx.respond(
            embed=hikari.Embed(
                title=f"{card['identifier']} Sent!",
                description=f"The card has been sent to {target.mention}.",
                color=0x00FF00
            )
            .set_image(
                hikari.Bytes(
                    image,
                    "image.png",
                )
            )
        )
    else:
        await ctx.respond(
            embed=hikari.Embed(
                title="Error!",
                description="There was an error while sending the card.",
                color=0xFF0000
            )
        )

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
