from library.database import bakesale, dbuser
from cogs.bakesale.group import group
from library import decorators as dc
import lightbulb
import hikari

plugin = lightbulb.Plugin(__name__)

@group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    name="offer_id",
    description="What's the ID of the offer?",
    required=True,
    type=hikari.OptionType.INTEGER,
    min_value=0,
)
@lightbulb.add_checks(
    lightbulb.guild_only
)
@lightbulb.command(name='remove', description="Remove an item offer you put out!", pass_options=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
@dc.prechecks('bakesale remove')
async def bot_command(ctx: lightbulb.SlashContext, offer_id):
    offer = bakesale.get_offer(offer_id)
    bakesale.delete_offer(offer_id)
    dbuser.userdb(ctx.user.id).add_to_inventory(
        card_id=offer['card_id'],
        amount=offer['amount'],
        allow_limited=True
    )
    await ctx.respond(
        hikari.Embed(
            title="Offer Withdrawn",
            description=f"Your offer to the market for {offer['amount']}x {ctx.bot.d['coin_name']['normal']}s `{offer['card_id']}` cards was withdrawn."
        )
    )

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
