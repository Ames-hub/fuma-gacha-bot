from library import decorators as dc
from cogs.staff.group import group
from library import database
import lightbulb
import hikari

plugin = lightbulb.Plugin(__name__)

@group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    name="reason",
    description="Why're they being banned?",
    required=True,
    min_length=20,
    type=hikari.OptionType.STRING
)
@lightbulb.option(
    name="user",
    description="Who's going?",
    required=True,
    type=hikari.OptionType.USER,
)
@lightbulb.add_checks(
    lightbulb.guild_only
)
@lightbulb.command(name='ban_user', description="Ban a user from using the bot (bot admin only)", pass_options=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
@dc.check_admin_status()
@dc.check_bot_ban()
async def bot_command(ctx: lightbulb.SlashContext, user: hikari.User, reason: str):
    success = database.set_user_ban(
        ban_status=True,
        user_id=int(user.id),
        reason=str(reason),
    )

    if success:
        await ctx.respond(
            embed=hikari.Embed(
                title="Success!",
                description=f"User {user.mention} has been banned.",
            )
            .add_field(
                name="Reason",
                value=reason,
                inline=True,
            )
            .add_field(
                name="duration",
                value="forever",
                inline=True,
            )
        )
    else:
        await ctx.respond(
            embed=hikari.Embed(
                title="Uh oh!",
                description=f"User {user.mention} has not been banned. Please contact the developer.",
                color=0xff0000,
            ),
            flags=hikari.MessageFlag.EPHEMERAL
        )

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
