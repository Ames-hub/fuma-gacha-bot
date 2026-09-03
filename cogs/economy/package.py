from library.database import economy, dbcards
from cogs.economy.bakery_group import group
from library import decorators as dc
import lightbulb
import hikari

plugin = lightbulb.Plugin(__name__)

@group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.add_checks(
    lightbulb.guild_only
)
@lightbulb.command(name='package', description="Package bakery products for a good payday!", pass_options=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
@dc.prechecks('package', cooldown_s=1800)  # 30 minutes
async def bot_command(ctx: lightbulb.SlashContext):
    target_acc = economy.account(ctx.author.id)

    all_limited_cards = dbcards.filtered_get_card(card_tier=3, fetch_one=False)
    if len(all_limited_cards) == 0:
        await ctx.respond(
            hikari.Embed(
                title="Nothing to do..,",
                description="Hmm.. looks like packaging was all done, maybe check back later.",
                colour=ctx.bot.d['branding']['embed']
            )
            .set_footer("Hint: This command is only available when limited edition cards are running!")
        )

    payout = 2

    embed = (
        hikari.Embed(
            title="Products packaged!",
            description=f"You spent some time wrapping up bread, biscuits, and other items.",
            colour=ctx.bot.d['branding']['embed']
        )
        .add_field(
            name="Payout!",
            value=f"You got {payout} {ctx.bot.d['coin_name']['better']}s!"
        )
    )

    target_acc.normalcoin.modify_balance(payout, "+")

    await ctx.respond(embed)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
