from library.database import dbuser
from library.botapp import botapp
from library.commands import cmd
import functools
import lightbulb
import datetime
import hikari

def prechecks(cmd_id, cooldown_s=0):
    """
    Checks all basic preconditions for the bot to allow the user to use the command.
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(ctx: lightbulb.SlashContext, *args, **kwargs):
            if not type(ctx) == lightbulb.SlashContext:
                raise TypeError("This decorator can only be used on slash commands!")
            if dbuser.run_ban_check(int(ctx.author.id)) is True:
                await ctx.respond(
                    embed=hikari.Embed(
                        title="Forbidden",
                        description="Sorry, you can't access this bot anymore.",
                        color=0xff0000,
                    )
                )
                return None

            is_enabled = cmd(cmd_id).is_enabled()
            if not is_enabled:
                await ctx.respond(
                    embed=hikari.Embed(
                        title="Forbidden",
                        description="Sorry, this command is temporarily disabled.",
                    )
                )
                return None

            if cooldown_s != 0:
                # Cooldown system
                timenow = datetime.datetime.now().timestamp()
                last_used = botapp.d['cooldowns'].get(ctx.author.id, {}).get(cmd_id, 0)

                if timenow < last_used + cooldown_s:
                    raise lightbulb.errors.CommandIsOnCooldown(
                        retry_after=last_used + cooldown_s - timenow
                    )

                botapp.d['cooldowns'].setdefault(ctx.author.id, {})[cmd_id] = timenow

            return await func(ctx, *args, **kwargs)
        return wrapper
    return decorator

def check_admin_status():
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(ctx: lightbulb.SlashContext, *args, **kwargs):
            if not type(ctx) == lightbulb.SlashContext:
                raise TypeError("This decorator can only be used on slash commands!")
            if dbuser.is_administrator(list(ctx.member.role_ids), int(ctx.author.id)) is False:
                await ctx.respond(
                    embed=hikari.Embed(
                        title="Unauthorized",
                        description="This command is for bot staff only.",
                    ),
                    flags=hikari.MessageFlag.EPHEMERAL
                )
                return None
            return await func(ctx, *args, **kwargs)
        return wrapper
    return decorator