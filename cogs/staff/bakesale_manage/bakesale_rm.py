from cogs.staff.bakesale_manage.group import staff_bakesale_group
from library.database import bakesale, eventlogs, dbuser
from library import decorators as dc
import lightbulb
import hikari


plugin = lightbulb.Plugin(__name__)

@staff_bakesale_group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    name="offer_id",
    description="The offer ID for the bakesale to remove.",
    required=True,
    type=hikari.OptionType.INTEGER,
)
@lightbulb.command(name='remove', description="Forcefully delete an offer from the bakesale.")
@lightbulb.implements(lightbulb.SlashSubCommand)
@dc.check_admin_status()
@dc.prechecks('staff bakesale rm-item')
async def bot_command(ctx: lightbulb.SlashSubCommand):
    offer_id = ctx.options.offer_id
    # Refunds offer to the user.
    offer = bakesale.get_offer(offer_id)
    if not offer:
        await ctx.respond(
            hikari.Embed(
                title="Offer not found",
                description="That offer does not exist, did you get the offer ID right?"
            )
        )
        return
    bakesale.delete_offer(offer_id)
    dbuser.userdb(offer['seller_id']).add_to_inventory(
        card_id=offer['card_id'],
        amount=offer['amount'],
        allow_limited=True
    )

    await ctx.respond(
        hikari.Embed(
            title="Offer Removed",
            description=f"Offer `{offer_id}` was forcefully refunded back to <@{offer['seller_id']}> ({offer['seller_disp_name']})",
            colour=ctx.bot.d['branding']['embed']
        )
    )

    await eventlogs.log_event(
        f"Bakesale Offer Removed",
        f"The bakesale offer {offer_id} was removed from the market by {ctx.user.mention}"
    )

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
