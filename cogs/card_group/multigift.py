from library.dbmodules.dbcards import gift_errors
from library import decorators as dc
from library.database import dbcards
from library.botapp import botapp
import lightbulb
import hikari

plugin = lightbulb.Plugin(__name__)

@botapp.command()
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    name="card_id_list",
    description="A List of Cards to gift by their ID, separated by commas.",
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
    description="How many to send of each card.",
    required=True,
    type=hikari.OptionType.INTEGER,
    min_value=1,
)
@lightbulb.add_checks(
    lightbulb.guild_only
)
@lightbulb.command(name='multigift', description="Gift someone lots of different cards!", pass_options=True)
@lightbulb.implements(lightbulb.SlashCommand)
@dc.prechecks('card gift')
async def bot_command(ctx: lightbulb.SlashContext, card_id_list:str, target:int, amount:int):
    if target == ctx.author.id:
        await ctx.respond(
            embed=hikari.Embed(
                title="Self-gifting",
                description="You cannot gift yourself a card!",
                color=0xFF0000
            )
        )
        return
    elif target == botapp.get_me().id:
        await ctx.respond(
            embed=hikari.Embed(
                title="Invalid Target",
                description="While I appreciate the sentiment, you can't gift me a card ^^'",
                color=0xFF0000
            )
        )
        return

    card_id_list = [card_id.strip().replace(" ", "") for card_id in card_id_list.split(',')]
    errors_list = []
    success_count = 0

    for card_id in card_id_list:
        try:
            success = dbcards.gift_card(
                card_id=str(card_id),
                giver_id=int(ctx.author.id),
                receiver_id=int(target),
                giving_amount=int(amount),
            )
        except gift_errors.BadAmount as err:
            errors_list.append(f"The amount `{amount}` is invalid for the card with ID `{card_id}`.")
            continue
        except gift_errors.NotEnoughOfItem as err:
            errors_list.append(f"You do not have enough of the card with ID `{card_id}` to send {amount}.")
            continue
        except gift_errors.GiverDoesNotOwnCard as err:
            errors_list.append(f"You do not own the card with ID `{card_id}`.")
            continue
        except gift_errors.GiftDBError as err:
            errors_list.append(f"There was an error while sending the card with ID `{card_id}`: {str(err)}")
            continue

        if not success:
            errors_list.append(f"There was an unspecified error while sending the card with ID `{card_id}`.")
            continue
        else:
            success_count += 1

    embed = hikari.Embed(
        title=f"{success_count} Cards Sent!",
        description=f"You have sent {success_count} cards to <@{target}>.",
        colour=ctx.bot.d['branding']['embed']
    )

    if len(errors_list) != 0:
        embed.add_field(
            name="Some cards couldn't be sent",
            value="\n".join(errors_list),
            inline=False
        )

    await ctx.respond(embed)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
