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
    name="user",
    description="Who you want to see the wishlist for, defaults to you.",
    required=False,
    type=hikari.OptionType.USER,
    default=-1
)
@lightbulb.command(name='list', description="See your wishlist!", pass_options=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
@dc.prechecks('wishlist-list')
async def bot_command(ctx: lightbulb.SlashContext, user: hikari.User):
    if user == -1:
        user = ctx.user
    dbuser = userdb(user.id)
    wishlist = dbuser.wishlist.fetch()

    if wishlist is False:
        await ctx.respond(
            hikari.Embed(
                title="Error",
                description="For some reason, we could not read your wishlist. Please file a bug report!"
            )
        )
        return

    if user.id == ctx.user.id:
        embed = hikari.Embed(
            title="Your Wishlist! ✨"
        )
    else:
        embed = hikari.Embed(
            title=f"{user.display_name}'{'s' if not user.display_name.endswith('s') else ''} Wishlist! ✨"
        )

    string_list = []
    has_wanted_items = False
    for item in wishlist:
        card = dbcards.view_card(item['card_id'])[0]

        has_in_inventory = len(dbuser.get_inventory(card_id=item['card_id'])) > 0
        
        if has_in_inventory:
            string_list.append(f"- ✅  {card['name']} - `{item['card_id']}` - Wishlisted on {item['start_date']} | Obtained!\n")
            has_wanted_items = True
        else:
            string_list.append(f"- {card['name']} - `{item['card_id']}` - Wishlisted on {item['start_date']}\n")

    if len(string_list) > 0:
        embed.add_field(
            name=f"Wishlist of {len(string_list)} items",
            value="".join(string_list)
        )
    else:
        embed.add_field(
            name="No cards wishlisted!",
            value="Add some cards you want with `/wishlist add`"
        )

    if has_wanted_items:
        embed.set_footer("To get your obtained items off this list, run `/wishlist clean`")

    await ctx.respond(embed)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
