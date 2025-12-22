from library.database import dbuser
from library.botapp import botapp
from library.commands import cmd
import functools
import lightbulb
import datetime
import hikari
import time


def prechecks(cmd_id, cooldown_s=0):
    """
    Checks all basic preconditions for the bot to allow the user to use the command.
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(ctx: lightbulb.SlashContext, *args, **kwargs):
            if not isinstance(ctx, lightbulb.SlashContext):
                raise TypeError("This decorator can only be used on slash commands!")

            user_id = int(ctx.author.id)

            # Ban check
            if dbuser.run_ban_check(user_id):
                await ctx.respond(
                    embed=hikari.Embed(
                        title="Forbidden",
                        description="Sorry, you can't access this bot anymore.",
                        color=0xff0000,
                    )
                )
                return None

            # Command enabled check
            if not cmd(cmd_id).is_enabled():
                await ctx.respond(
                    embed=hikari.Embed(
                        title="Forbidden",
                        description="Sorry, this command is temporarily disabled.",
                    )
                )
                return None

            # Cooldown check
            if botapp.d['cooldowns_on'] is True:
                if cooldown_s > 0:
                    now = time.time()
                    user_cooldowns = botapp.d.setdefault("cooldowns", {}).setdefault(user_id, {})
                    expiry = user_cooldowns.get(cmd_id, 0)

                    if now < expiry:
                        raise lightbulb.errors.CommandIsOnCooldown(
                            retry_after=expiry - now
                        )

                    # Store expiry timestamp
                    user_cooldowns[cmd_id] = now + cooldown_s

            return await func(ctx, *args, **kwargs)
        return wrapper
    return decorator


def check_admin_status():
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(ctx: lightbulb.SlashContext, *args, **kwargs):
            if not isinstance(ctx, lightbulb.SlashContext):
                raise TypeError("This decorator can only be used on slash commands!")

            if not dbuser.is_administrator(list(ctx.member.role_ids), int(ctx.author.id)):
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
