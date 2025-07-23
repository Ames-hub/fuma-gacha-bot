from library.database import dbuser
import functools
import lightbulb
import hikari

def check_bot_ban():
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
            return await func(ctx, *args, **kwargs)
        return wrapper
    return decorator

def check_admin_status():
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(ctx: lightbulb.SlashContext, *args, **kwargs):
            if not type(ctx) == lightbulb.SlashContext:
                raise TypeError("This decorator can only be used on slash commands!")
            if dbuser.has_admin_role(ctx.member.role_ids) is False:
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