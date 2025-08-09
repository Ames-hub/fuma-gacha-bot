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
    length=10_080,  # 1 week in seconds.
    bucket=lightbulb.buckets.UserBucket,
    uses=1
)
@lightbulb.command(name='gymbattle', description="Fight for some money and cards!", pass_options=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
@dc.check_bot_ban()
async def bot_command(ctx: lightbulb.SlashContext):
    target_acc = economy.account(ctx.author.id)

    rare_cards = []
    for i in range(3):  # Get 3 random cards that are rare.
        try:
            card = dbcards.filtered_pull_card(
                filter_string="<rarity=5><card_tier=1><pullable=True>",
            )
        except dbcards.ItemNonexistence:
            rare_cards.append(False)
            continue
        rare_cards.append(card)

    gained_fc = random.randint(120, 320)
    target_acc.fumacoins.modify_balance(gained_fc, 'add')

    embed = (
        hikari.Embed(
            title="Gym Battle!",
            description=f"You fought many battles with gym leaders and won and lost some.\nEarned {gained_fc} FumaCoins!",
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
            value=f"You got 3 rare cards! {", ".join(str_rare_cards)}"
        )

    await ctx.respond(embed)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
