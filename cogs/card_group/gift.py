from library import decorators as dc
from library.database import dbcards
from library.botapp import botapp
import lightbulb
import hikari

plugin = lightbulb.Plugin(__name__)

@botapp.command()
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    name="name_or_id",
    description="The name or ID of the card. If using ID, prefix 'id:'",
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
@dc.check_bot_ban()
async def bot_command(ctx: lightbulb.SlashContext, name_or_id:str, target:hikari.Member, amount:int):
    success = dbcards.gift_card(
        cardname=str(name_or_id),
        giver_id=int(ctx.author.id),
        receiver_id=int(target),
        giving_amount=int(amount),
    )
    await ctx.respond(success)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
