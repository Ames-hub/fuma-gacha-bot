from library import decorators as dc
from cogs.staff.group import group
from library import database
import lightbulb
import hikari

plugin = lightbulb.Plugin(__name__)

@group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    name="user",
    description="Who's getting unbanned?",
    required=True,
    type=hikari.OptionType.USER,
)
@lightbulb.add_checks(
    lightbulb.guild_only
)
@lightbulb.command(name='unban_user', description="Allow a user to use the bot after being banned! (bot admin only)", pass_options=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
@dc.check_admin_status()
@dc.check_bot_ban()
async def bot_command(ctx: lightbulb.SlashContext, user: hikari.User):
    success = database.set_user_ban(
        ban_status=False,
        user_id=int(user.id),
    )

    if success:
        await ctx.respond(
            embed=hikari.Embed(
                title="Success!",
                description=f"User {user.mention} has been unbanned.",
            )
        )

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
