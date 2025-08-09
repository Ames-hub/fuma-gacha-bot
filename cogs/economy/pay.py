from cogs.economy.group import group
from library.database import economy
from library import decorators as dc
import lightbulb
import hikari

plugin = lightbulb.Plugin(__name__)

@group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.add_checks(
    lightbulb.guild_only
)
@lightbulb.option(
    name="user",
    description="Who are you sending the money to?",
    required=True,
    type=hikari.OptionType.USER,
)
@lightbulb.option(
    name="amount",
    description="How much are you sending?",
    required=True,
    type=hikari.OptionType.INTEGER,
    min_value=1,
)
@lightbulb.option(
    name="coin_type",
    description="What kind of coins are you sending?",
    required=True,
    choices=["FumaCoin", "NichoCoin"],
    type=hikari.OptionType.STRING,
)
@lightbulb.command(name='pay', description="Send some money to someone!", pass_options=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
@dc.check_bot_ban()
async def bot_command(ctx: lightbulb.SlashContext, coin_type: str, amount: int, user: hikari.User):
    sender_acc = economy.account(ctx.author.id)
    target_acc = economy.account(user.id)

    if coin_type == "FumaCoin":
        send_ok = sender_acc.fumacoins.modify_balance(amount, 'subtract')
        tgt_ok = target_acc.fumacoins.modify_balance(amount, 'add')
    else:
        send_ok = sender_acc.nichocoins.modify_balance(amount, 'subtract')
        tgt_ok = target_acc.nichocoins.modify_balance(amount, 'add')

    if send_ok and tgt_ok:
        await ctx.respond(
            embed=(
                hikari.Embed(
                    title="Money Sent!",
                    description=f"You have sent {amount} {coin_type}s to {user.mention}.",
                    color=0x00ff00,
                )
            )
        )
    else:
        await ctx.respond(
            embed=(
                hikari.Embed(
                    title="Error!",
                    description="There was an error while sending the money. Its been sent back.",
                    color=0xff0000,
                )
            )
        )
        if coin_type == "FumaCoin":
            sender_acc.fumacoins.modify_balance(amount, 'add')
            target_acc.fumacoins.modify_balance(amount, 'subtract')
        else:
            sender_acc.nichocoins.modify_balance(amount, 'add')
            target_acc.nichocoins.modify_balance(amount, 'subtract')

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
