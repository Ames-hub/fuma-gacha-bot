from library.dbmodules.notifications import set_notifs, send_notification
from library import decorators as dc
from cogs.notifs.group import group
import lightbulb
import hikari

plugin = lightbulb.Plugin(__name__)

@group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    name="status",
    description="Do you want notifications or not?",
    required=True,
    choices=['Notifications On', 'No Notifications'],
    type=hikari.OptionType.STRING,
)
@lightbulb.add_checks(
    lightbulb.guild_only
)
@lightbulb.command(name='toggle', description="Toggle on/off notifications.", pass_options=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
@dc.prechecks('notifs toggle')
async def bot_command(ctx: lightbulb.SlashContext, status:str):
    status = True if status == "Notifications On" else False
    success = set_notifs(ctx.author.id, state=status)
    if success:
        await ctx.respond(
            embed=(
                hikari.Embed(
                    title="Notifications On",
                    description="You'll start hearing from us from now on!\nPlease make sure we're able to DM you! (you can use `/notif test` to check!)"
                )
                .set_footer(
                    text="By leaving this setting on, you agree to us contacting you for the purpose of these notifications."
                )
            )
        )
        await send_notification(ctx.author.id, msg_body="You've enabled notifications!")
    else:
        await ctx.respond(
            hikari.Embed(
                title="Error!",
                description="Couldn't enable notifications!"
            )
        )

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
