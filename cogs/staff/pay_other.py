from library.database import dbuser, eventlogs
from cogs.staff.group import staff_group
from library import decorators as dc
import lightbulb
import hikari


plugin = lightbulb.Plugin(__name__)

@staff_group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    name="target_user",
    description="The user who you wish to give the coins to.",
    required=True,
    type=hikari.OptionType.MENTIONABLE,
)
@lightbulb.option(
    name="bal_type",
    description="Better coins or normal coins?",
    choices=[
        "Donut Coins",
        "Woonagi Points"
    ],
    required=True,
    type=hikari.OptionType.STRING,
)
@lightbulb.option(
    name="amount",
    description="The amount of coins to give to the user.",
    required=True,
    type=hikari.OptionType.INTEGER,
    min_value=1,
)
@lightbulb.add_checks(
    lightbulb.guild_only
)
@lightbulb.command(name='pay', description="Pay a user some coins of some sort.", pass_options=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
@dc.check_admin_status()
@dc.prechecks('staff pay')
async def bot_command(ctx: lightbulb.SlashContext, target_user: hikari.Member, bal_type:str, amount: int):
    user = dbuser.userdb(target_user)
    if bal_type == "Donut Coins":
        user.bank.normalcoin.modify_balance(amount, "+")
    else:
        user.bank.bettercoin.modify_balance(amount, "+")

    await ctx.respond(
        hikari.Embed(
            title="Paid!",
            description=f"{amount} {bal_type} paid to <@{target_user}>"
        )
    )

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
