from library.database import stdn_events, eventlogs
from cogs.staff.events.group import event_group
from library import decorators as dc
import lightbulb
import hikari

plugin = lightbulb.Plugin(__name__)

@event_group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    name="unique",
    description="Is this event only going to happen once?",
    required=True,
    type=hikari.OptionType.BOOLEAN,
)
@lightbulb.option(
    name="name",
    description="What's the name or title for this event?",
    required=True,
    type=hikari.OptionType.STRING
)
@lightbulb.add_checks(
    lightbulb.guild_only
)
@lightbulb.command(name='create', description="Create a new event that can be scheduled", pass_options=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
@dc.check_admin_status()
@dc.prechecks('event_make')
async def bot_command(ctx: lightbulb.SlashContext, name, unique):
    try:
        success = stdn_events.create(
            name=name,
            onetime=unique
        )
    except stdn_events.EventExistingError:
        await ctx.respond(
            embed=hikari.Embed(
                title="Event Existant",
                description="There's already an event with that name.\nPlease choose another name.",
                color=0xff0000,
            ),
        )
        return

    if success:
        embed=(
            hikari.Embed(
                title="Success!",
                description="The event has been created and is ready to be scheduled for any time.\n\n"
                            f"To schedule the event,\nuse `/staff event schedule` command.",
                color=0x00ff00,
            )
        )

        if unique:
            embed.add_field(
                name="Unique Event",
                value="This event is only going to happen once.\n"
                      "Once ended, it will not be able to be rescheduled.\n",
                inline=False,
            )

        await ctx.respond(embed)

        await eventlogs.log_event(
            "Event Created",
            f"The event {name} has been created."
        )
    else:
        await ctx.respond(
            embed=hikari.Embed(
                title="Error!",
                description="The event could not be created.",
                colour=0xff0000,
            )
        )

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
