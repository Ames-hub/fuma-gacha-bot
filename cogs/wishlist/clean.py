from cogs.wishlist.group import wishlist_group
from library.dbmodules.dbuser import userdb
from library.dbmodules import dbcards
from library import decorators as dc
import lightbulb
import hikari


plugin = lightbulb.Plugin(__name__)

@wishlist_group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    name="do_all_items",
    description="This sets if we purge EVERYHING, opposed to just what you have obtained thats on the list.",
    required=False,
    default=False,
    type=hikari.OptionType.BOOLEAN
)
@lightbulb.command(name='clean', description="Clean up the wishlist, so all the cards on it that you've obtained are cleared from it!", pass_options=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
@dc.prechecks('wishlist-clean')
async def bot_command(ctx: lightbulb.SlashContext, do_all_items:bool):
    user = userdb(ctx.user.id)
    wishlist = user.wishlist.fetch()

    if wishlist is False:
        await ctx.respond(
            hikari.Embed(
                title="Error",
                description="For some reason, we could not read your wishlist. Please file a bug report!"
            )
        )
        return

    for item in wishlist:
        has_in_inventory = len(user.get_inventory(card_id=item['card_id'])) > 0        
        if do_all_items:
            user.wishlist.remove(item['card_id'])
        else:
            if has_in_inventory:
                user.wishlist.remove(item['card_id'])

    embed = hikari.Embed(
        title="Wishlist cleared!",
        description="All the cards you wanted and obtained were cleaned from the list." if not do_all_items else "Every item removed from your wishlist."
    )

    await ctx.respond(embed)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
