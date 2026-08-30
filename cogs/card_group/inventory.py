from library import decorators as dc
from library.database import dbuser
from library.botapp import botapp
import lightbulb
import hikari
import math

plugin = lightbulb.Plugin(__name__)

ITEMS_PER_PAGE = 10

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
    required=True,
    type=hikari.OptionType.INTEGER,
    min_value=1,
)
@lightbulb.add_checks(
    lightbulb.guild_only
)
@lightbulb.command(name='inv', description="See your current inventory!", pass_options=True)
@lightbulb.implements(lightbulb.SlashCommand)
@dc.prechecks('inventory')
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
                      f" assosciated with {card_group if card_group is not None else "any"} group, at {f"rarity {card_rarity}" if card_rarity is not None else "any rarity"} with "
                      f"{f"the ID \"{card_id}\"" if card_id is not None else 'any ID.'}")
    else:
        search_txt = "Showing your inventory."

    total_items = len(inventory)
    total_pages = max(1, math.ceil(total_items / ITEMS_PER_PAGE))

    # Clamp to the last valid page instead of erroring.
    if page_number >= total_pages:
        page_number = total_pages - 1
    if page_number < 0:
        page_number = 0

    item_ids = list(inventory.keys())
    start_index = page_number * ITEMS_PER_PAGE
    end_index = start_index + ITEMS_PER_PAGE
    page_item_ids = item_ids[start_index:end_index]

    invent_str = f"Your Inventory has {total_items} Items."
    for item_identifier in page_item_ids:
        rarity_txt = plugin.bot.d['rarity_emojis_text'][inventory[item_identifier]['rarity']]
        invent_str += (
            f"\n{rarity_txt} *__{inventory[item_identifier]['name']}__* - group: {inventory[item_identifier]['group']} "
            f"- `{item_identifier}`\n**Amount** {inventory[item_identifier]['amount']}\n"
        )
        if inventory[item_identifier]['tier'] > 1:
            invent_str += f"**Card Tier** {botapp.d['card_tier_names']['numeric'][inventory[item_identifier]['tier']]}\n"

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
            description=invent_str,
            colour=ctx.bot.d['branding']['embed']
        )
    )

    footer_text = ""
    if is_search is True:
        footer_text += f"{search_txt}\n"
    footer_text += f"Page {page_number + 1}/{total_pages} • {total_items} total items"

    embed.set_footer(text=footer_text)

    await ctx.respond(embed=embed)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)