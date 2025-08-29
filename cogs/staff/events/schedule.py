from library.database import stdn_events, eventlogs, TimeError
from cogs.staff.events.group import event_group
from library import decorators as dc
import lightbulb
import hikari

plugin = lightbulb.Plugin(__name__)

@event_group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    name="end_time",
    description="When's the exact moment that it should end?",
    required=True,
    type=hikari.OptionType.STRING,
)
@lightbulb.option(
    name="start_time",
    description="What's the exact moment that it should start?",
    required=True,
    type=hikari.OptionType.STRING,
)
@lightbulb.option(
    name="name",
    description="What's the name or title of this event?",
    required=True,
    type=hikari.OptionType.STRING
)
@lightbulb.add_checks(
    lightbulb.guild_only
)
@lightbulb.command(name='schedule', description="Schedule a new event", pass_options=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
@dc.check_admin_status()
@dc.prechecks('event_schedule')
async def bot_command(ctx: lightbulb.SlashContext, name, start_time, end_time):
    try:
        success = stdn_events.schedule(
            name=name,
            start_time=start_time,
            end_time=end_time
        )
    except TimeError:
        await ctx.respond(
            embed=hikari.Embed(
                title="Time Format Error",
                description="You have entered an invalid time format.\n"
                            "Expected Format: DD/MM/YYYY HH:MM AM/PM\n"
                            "It must be matched exactly.\n"
                            "Example: 04/12/2024 12:00 AM",
                color=0xff0000,
            ),
            flags=hikari.MessageFlag.EPHEMERAL
        )
        return
    except stdn_events.EventSchedulingError:
        await ctx.respond(
            embed=hikari.Embed(
                title="Event scheduling",
                description="There's already an event scheduled for then.",
                color=0xff0000,
            ),
        )
        return
    except stdn_events.NotSchedulable:
        await ctx.respond(
            embed=hikari.Embed(
                title="Event scheduling",
                description="This event is no longer schedulable.",
                color=0xff0000,
            ),
        )
        return

    if success:
        await ctx.respond(
            embed=hikari.Embed(
                title="Success!",
                description="The event has been scheduled.",
            )
        )

        await eventlogs.log_event(
            "Event Scheduled",
            f"The event {name} has been scheduled for {start_time} to {end_time}."
        )
    else:
        await ctx.respond(
            embed=hikari.Embed(
                title="Error!",
                description="The event could not be scheduled.",
            )
        )

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
