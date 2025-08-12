from library import decorators as dc
from library.database import dbuser
from library.botapp import botapp
import lightbulb
import hikari

plugin = lightbulb.Plugin(__name__)

@botapp.command()
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    name="query",
    description="Search your inventory by card name.",
    required=False,
    type=hikari.OptionType.STRING,
    default=None
)
@lightbulb.option(
    name="user",
    description="Check a particular persons inventory.",
    required=False,
    type=hikari.OptionType.MENTIONABLE,
    default=None
)
@lightbulb.option(
    name="page",
    description="Enter which page of your inventory you want!",
    required=False,
    type=hikari.OptionType.INTEGER,
    min_value=1,
    default=1
)
@lightbulb.add_checks(
    lightbulb.guild_only
)
@lightbulb.command(name='inv', description="See your current inventory!")
@lightbulb.implements(lightbulb.SlashCommand)
@dc.prechecks()
async def bot_command(ctx: lightbulb.SlashContext):
    search = ctx.options.query
    page_number = int(ctx.options.page) - 1  # index at 0.
    target_user: hikari.Member = ctx.options.user

    inventory = dbuser.get_inventory(ctx.author.id if target_user is None else int(target_user), search)

    invent_str = f"Your Inventory has {len(inventory)} Items."
    for item_identifier in inventory:
        invent_str += f"\n*__{inventory[item_identifier]['name']}__* - {item_identifier}\n**Amount** {inventory[item_identifier]['amount']}\n"

    lines = invent_str.split("\n")

    # One chunk every 300 lines
    chunk_size = 300
    chunk_list = ["\n".join(lines[i:i+chunk_size]) for i in range(0, len(lines), chunk_size)]

    if page_number > len(chunk_list):
        page_number = len(chunk_list)

    if target_user is not None:
        if botapp.d['inventory_username_cache'].get(target_user) is None:
            target_user = await botapp.rest.fetch_member(ctx.guild_id, target_user)
            target_username = target_user.username
        else:
            target_username = botapp.d['inventory_username_cache'].get(target_user.id)
    else:
        target_username = ctx.author.username

    embed = (
        hikari.Embed(
            title=f"{target_username}'s Inventory",
            description=chunk_list[page_number],
        )
    )

    footer_text = ""
    if search is not None:
        footer_text += f"Search filtered with query: {search}\n"
    if len(chunk_list) > 1:
        footer_text += "Your inventory contains too many items to show on one page, use page option to see more."

    if footer_text != "":
        embed.set_footer(text=footer_text)

    await ctx.respond(embed=embed)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
