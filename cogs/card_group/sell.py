from library.dbmodules.dbcards import view_card
from library.dbmodules.dbuser import userdb
from library import decorators as dc
from library.botapp import botapp
import lightbulb
import hikari
import random

plugin = lightbulb.Plugin(__name__)

def determine_value(card:dict):
    card_tier = card['card_tier']
    if card_tier == 1:
        value_dict = {
            1: (200, 400),
            2: (300, 600),
            3: (400, 800),
            4: (500, 1000),
            5: (2500, 5000),
        }
        rarity_val = random.randint(value_dict[card['rarity']][0], value_dict[card['rarity']][1])
        return rarity_val
    elif card['birthday_flag']:
        return random.randint(10_000, 20_000)
    elif card_tier == 2:
        return random.randint(15_000, 30_000)
    elif card_tier == 3:
        return random.randint(35_000, 70_000)

@botapp.command()
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    "card_id",
    "The ID of the card you want to sell.",
    type=hikari.OptionType.STRING,
    required=True,
)
@lightbulb.option(
    "amount",
    "The amount of the specified card you want to sell.",
    type=hikari.OptionType.INTEGER,
    required=True,
)
@lightbulb.command(name="sell", description="Easily Sell a card for some money!")
@lightbulb.implements(lightbulb.SlashCommand)
@dc.prechecks("sell")
async def bot_command(ctx: lightbulb.SlashContext):
    card_id = ctx.options.card_id
    user = userdb(ctx.user.id)
    card = view_card(card_id)
    if not card:
        await ctx.respond(
            hikari.Embed(
                title="Card not found!",
                description="This card does not exist.",
                colour=ctx.bot.d['branding']['embed']
            )
        )
        return
    card = card[0]
    
    inv_card = user.get_inventory(ctx.options.card_id)[ctx.options.card_id]
    if ctx.options.amount > inv_card['amount']:
        await ctx.respond(
            hikari.Embed(
                title="Too few cards!",
                description=f"You're trying to sell more cards than you have. You have {inv_card['amount']}",
                colour=ctx.bot.d['branding']['embed']
            )
        )
 
    gained_amount = int(determine_value(card) * ctx.options.amount)
    user.bank.normalcoin.modify_balance(gained_amount, "+")
    user.remove_from_inventory(card_id, ctx.options.amount)

    embed = (
        hikari.Embed(
            title="Card Sold",
            description=f"You sold {ctx.options.amount}x `{card_id}` for {gained_amount} {ctx.bot.d['coin_name']['normal']}s",
            colour=ctx.bot.d['branding']['embed']
        )
    )

    await ctx.respond(embed=embed)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
