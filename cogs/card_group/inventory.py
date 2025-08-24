from library import decorators as dc
from library.database import dbuser
from library.botapp import botapp
import lightbulb
import hikari

plugin = lightbulb.Plugin(__name__)

@botapp.command()
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    name="card_rarity",
    description="Search your inventory by card rarity.",
    required=False,
    type=hikari.OptionType.INTEGER,
    default=None
)
@lightbulb.option(
    name="card_tier",
    description="Search your inventory by card tier.",
    required=False,
    type=hikari.OptionType.INTEGER,
    default=None
)
@lightbulb.option(
    name="card_group",
    description="Search your inventory by card group.",
    required=False,
    type=hikari.OptionType.STRING,
    default=None
)
@lightbulb.option(
    name="card_name",
    description="Search your inventory by card name.",
    required=False,
    type=hikari.OptionType.STRING,
    default=None
)
@lightbulb.option(
    name="card_id",
    description="Search your inventory by card ID.",
    required=False,
    type=hikari.OptionType.STRING,
    default=None
)
@lightbulb.option(
    name="target_user",
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
@lightbulb.command(name='inv', description="See your current inventory!", pass_options=True)
@lightbulb.implements(lightbulb.SlashCommand)
@dc.prechecks()
async def bot_command(ctx: lightbulb.SlashContext, page, target_user, card_id, card_name, card_group, card_tier, card_rarity):
    page_number = int(page) - 1  # index at 0.

    is_search = card_id is not None or card_name is not None or card_group is not None or card_rarity is not None or card_tier is not None
    inventory = dbuser.get_inventory(
        user_id=ctx.author.id if target_user is None else int(target_user),
        card_id=card_id,
        card_name=card_name,
        card_group=card_group,
        card_rarity=card_rarity,
        card_tier=card_tier,
    )
    if is_search:
        search_txt = (f"Searching for a tier {card_tier if card_tier is not None else "any"} card with {card_name if card_name is not None else "any"} name,"
                      f" assosciated with {card_group if card_group is not None else "any"} group, at {f"rarity {card_rarity}" if card_rarity is not None else "any rarity"} with"
                      f"{f"the ID \"{card_id}\"" if card_id is not None else 'any ID.'}")
    else:
        search_txt = "Showing your inventory."

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
    if is_search is True:
        footer_text += f"{search_txt}\n"
    if len(chunk_list) > 1:
        footer_text += "Your inventory contains too many items to show on one page, use page option to see more."

    if footer_text != "":
        embed.set_footer(text=footer_text)

    await ctx.respond(embed=embed)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
