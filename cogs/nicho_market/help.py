from cogs.nicho_market.group import group
from library import decorators as dc
import lightbulb
import hikari

plugin = lightbulb.Plugin(__name__)

@group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.add_checks(
    lightbulb.guild_only
)
@lightbulb.command(name='help', description="Browse the public card market!", pass_options=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
@dc.prechecks('nicho help')
async def bot_command(ctx: lightbulb.SlashContext):
    await ctx.respond(
        embed=hikari.Embed(
            title="Nicho Shop Help",
            description="This is a basic guide to what the nichomarket is!"
        )
        .add_field(
            name="Purpose",
            value="Buy and sell cards! From users, for users. In other words, a card trading market."
        )
        .add_field(
            name="How to use",
            value="If you're looking to buy, use `/nicho market` to browse the market!\n"
                  "However, if you're looking to sell, use `/nichomarket sell` and we can get it on the market :)"
        )
        .add_field(
            name="Offer IDs",
            value="The offer ID is a unique identifier for each offer. It's used to identify the offer.\n"
                  "When you sell a card, it will give the offer an ID and that is the ID used to purchase the offer."
        )
        .add_field(
            name="I just sold, When do I get paid",
            value="After you sell a card on the market, you will have to wait until someone decides to buy the card.\n"
                  "Which may or may not happen. But if it does, once they buy the card, you will be paid!"
        )
    )

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
