from library.dbmodules.notifications import send_notification
from library import decorators as dc
from cogs.notifs.group import group
import lightbulb
import hikari

plugin = lightbulb.Plugin(__name__)

@group.child
@lightbulb.app_command_permissions(dm_enabled=True)
@lightbulb.command(name='test', description="Test to see if you can receive notifications!", pass_options=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
@dc.prechecks('notifs test')
async def bot_command(ctx: lightbulb.SlashContext):
    success = await send_notification(ctx.author.id, "You've asked us to test if you can get notifications, did you get this one? Hope so!")
    if success:
        await ctx.respond((
                hikari.Embed(
                    title="Success!",
                    description="Our systems report the test went well, you should've received a DM from us!"
                )
                .add_field(
                    name="Didn't get it?",
                    value="Please make sure we're not blocked by you and DMs are enabled. If it still fails, please contact support."
                )
            ),
            flags=hikari.MessageFlag.EPHEMERAL
        )
    else:
        await ctx.respond(
            hikari.Embed(
                title="Failure!",
                description="Our systems report the test failed! We couldn't send anything.\n"
                "Please make sure we're not blocked by you and DMs are enabled. If it still fails, please contact support."
            ),
            flags=hikari.MessageFlag.EPHEMERAL
        )

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
