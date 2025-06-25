from library.botapp import botapp
import lightbulb
import logging
import hikari

plugin = lightbulb.Plugin(__name__)

# For some reason, using plugin.listener doesn't work
@botapp.listen(lightbulb.CommandErrorEvent)
async def on_error(event: lightbulb.CommandErrorEvent) -> None:
    if not isinstance(event.exception, lightbulb.errors.CommandIsOnCooldown):
        logging.info("Error handler firing for unhandled exception.")

    if isinstance(event.exception, lightbulb.MissingRequiredPermission):
        embed = (
            hikari.Embed(
                title="Insufficient permissions",
                description="You do not have permission to use this command!",
            )
        )
        await event.context.respond(
            embed,
            flags=hikari.MessageFlag.EPHEMERAL
        )
        return
    elif isinstance(event.exception, lightbulb.MissingRequiredRole):
        await event.context.respond("You don't have the required role to run this command.", flags=hikari.MessageFlag.EPHEMERAL)
        return
    elif isinstance(event.exception, lightbulb.BotMissingRequiredPermission):
        await event.context.respond("I don't have the required permissions to run this command!", flags=hikari.MessageFlag.EPHEMERAL)
        return
    elif isinstance(event.exception, lightbulb.errors.OnlyInDM):
        await event.context.respond("This command can only be run in DMs.", flags=hikari.MessageFlag.EPHEMERAL)
        return
    elif isinstance(event.exception, lightbulb.errors.OnlyInGuild):
        await event.context.respond("This command can only be run in a guild.", flags=hikari.MessageFlag.EPHEMERAL)
        return
    elif isinstance(event.exception, lightbulb.errors.NotOwner):
        await event.context.respond("You are not the owner of this bot.", flags=hikari.MessageFlag.EPHEMERAL)
        return
    elif isinstance(event.exception, lightbulb.errors.CommandIsOnCooldown):
        embed = (
            hikari.Embed(
                title="Command is on cooldown",
                description=f"You have {event.exception.retry_after:.2f} seconds left before you can run this command again."
            )
        )
        await event.context.respond(embed)
        return
    elif isinstance(event.exception, hikari.errors.NotFoundError):
        logging.warning("An unintended keep-alive timeout for a command occured!")
        return
    else:
        print(f"An error occurred while running a command: {event.exception}")
        logging.error(f"An error occurred while running a command: {event.exception}", exc_info=event.exception)
        raise event.exception
    
def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
