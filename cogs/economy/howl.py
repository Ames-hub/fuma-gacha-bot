from library.database import economy, dbcards
from cogs.economy.group import group
from library import decorators as dc
import lightbulb
import hikari
import random

plugin = lightbulb.Plugin(__name__)

@group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.add_checks(
    lightbulb.guild_only
)
@lightbulb.add_cooldown(
    length=2_678_400,  # 1 Month in seconds.
    bucket=lightbulb.buckets.UserBucket,
    uses=1
)
@lightbulb.command(name='howl', description="Earn some rare cards, fumacoins and nichocoins!", pass_options=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
@dc.check_bot_ban()
async def bot_command(ctx: lightbulb.SlashContext):
    target_acc = economy.account(ctx.author.id)

    rare_cards = []
    for i in range(6):  # Get 6 random cards that are rare.
        try:
            card = dbcards.filtered_pull_card(
                filter_string="<rarity=5><card_tier=1><pullable=True>",
            )
        except dbcards.ItemNonexistence:
            rare_cards.append(False)
            continue
        rare_cards.append(card)

    try:
        event_card = dbcards.filtered_pull_card(
            filter_string="<card_tier=2><pullable=True>",
        )
    except dbcards.ItemNonexistence:
        event_card = False

    gained_fc = random.randint(300, 500)
    target_acc.fumacoins.modify_balance(gained_fc, 'add')

    gained_nc = random.randint(2, 12)
    target_acc.nichocoins.modify_balance(gained_nc, 'add')

    embed = (
        hikari.Embed(
            title="Howl!",
            description=f"You earned {gained_fc} FumaCoins and {gained_nc} NichoCoins!",
        )
    )

    str_rare_cards = [str(item) for item in rare_cards]
    if False in rare_cards:
        embed.add_field(
            name="Sorry!",
            value="It seems that for one or more of the cards we gave you, we couldn't because none were fit!\n\n"
                  f"The cards you got were:\n{", ".join(str_rare_cards)}"
        )
    else:
        embed.add_field(
            name="~ Rare Cards ~",
            value=f"You got 6 rare cards! {", ".join(str_rare_cards)}"
        )

    if event_card is False:
        embed.add_field(
            name="Event card",
            value="Sorry, but we couldn't find any event cards for you to take home!"
        )
    else:
        embed.add_field(
            name="~ Event Card ~",
            value=f"You got a new event card! \"{event_card['name']}\".\nID {event_card['identifier']}"
        )

    await ctx.respond(embed)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
