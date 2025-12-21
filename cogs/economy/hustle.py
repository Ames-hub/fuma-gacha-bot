from library.database import economy, dbcards
from cogs.economy.bakery_group import group
from library import decorators as dc
import lightbulb
import hikari
import random

plugin = lightbulb.Plugin(__name__)

# -----------------------------
# Splash text configuration
# -----------------------------

SPLASH_TEXTS = [
    {
        "min": 900,
        "max": 1000,
        "texts": [
            "You tripped over a sack of flour and accidentally sold the mess as 'artisan'. Somehow earned {coins} FumaCoins.",
            "You burned everything, cried a little, and a customer tipped you {coins} FumaCoins out of sympathy.",
            "You forgot the recipe entirely and improvised. The bakery survived. Barely. +{coins} FumaCoins."
        ]
    },
    {
        "min": 1101,
        "max": 1200,
        "texts": [
            "You worked the ovens all day and scraped together {coins} FumaCoins in sales.",
            "Your pastries were uneven but heartfelt. Customers paid you {coins} FumaCoins anyway.",
            "You undercharged, overworked, and still walked away with {coins} FumaCoins."
        ]
    },
    {
        "min": 1201,
        "max": 1300,
        "texts": [
            "Your timing was perfect and the bread sold fast. You earned {coins} FumaCoins.",
            "You nailed a new recipe and customers came back for seconds. +{coins} FumaCoins.",
            "The bakery smelled incredible today. Sales climbed to {coins} FumaCoins."
        ]
    },
    {
        "min": 1301,
        "max": 1399,
        "texts": [
            "You ran the bakery like a professional and pocketed {coins} FumaCoins.",
            "Your precision and consistency impressed regulars. They paid you {coins} FumaCoins.",
            "Everything went smoothly for once. You earned {coins} FumaCoins without disaster."
        ]
    },
    {
        "min": 1400,
        "max": 1499,
        "texts": [
            "Your pastries caused a line down the street. You pulled in {coins} FumaCoins.",
            "Customers spoke in hushed tones about your baking. Profits hit {coins} FumaCoins.",
            "You dominated the local market today. Competitors watched as you earned {coins} FumaCoins."
        ]
    },
    {
        "min": 1500,
        "max": 1500,
        "texts": [
            "You baked in silence and perfection followed. {coins} FumaCoins appeared.",
            "The money knew better than to not be in your wallet. {coins} FumaCoins came to you.",
            "The ovens obeyed you without question. Maximum profit: {coins} FumaCoins."
        ]
    }
]


def get_splash(coins: int) -> str:
    for tier in SPLASH_TEXTS:
        if tier["min"] <= coins <= tier["max"]:
            return random.choice(tier["texts"]).format(coins=coins)
    return "You worked the bakery and earned your pay."


# -----------------------------
# Command
# -----------------------------

@group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.command(
    name="hustle",
    description=f"Work the bakery for coins and a card!"
)
@lightbulb.implements(lightbulb.SlashSubCommand)
@dc.prechecks("bakery hustle", cooldown_s=86400)
async def bot_command(ctx: lightbulb.SlashContext):
    user_account = economy.account(ctx.author.id)

    money_gained = random.randint(900, 1500)
    failed = random.random() < 0.01  # 1% failure chance
    if failed:
        loss = money_gained // 2
        splash_text = (
            "You threw water at an oil fire and burnt down the bakery. "
            f"A Thief then walked by, slapped you, and stole {loss} FumaCoins from your wallet after giving you a mocking Nelson laugh."
        )
        user_account.fumacoins.modify_balance(loss, operator="-")
        embed_colour = 0xFF0000
    else:
        splash_text = get_splash(money_gained)
        user_account.fumacoins.modify_balance(money_gained, operator="+")
        embed_colour = 0x00FF00

    # -----------------------------
    # Card reward
    # -----------------------------

    if not failed:
        obtained_card = dbcards.pull_random_card()
        img_bytes = dbcards.load_img_bytes(obtained_card["identifier"])

        if obtained_card["rarity"] >= 3 or obtained_card["tier"] > 1:
            embed_colour = 0x00FF00

        image = hikari.Bytes(img_bytes, f"{obtained_card['name']}.png")
    else:
        image = hikari.URL('https://i.ytimg.com/vi/eOifa1WrOnQ/maxresdefault.jpg', 'nelson_laughing')

    embed = (
        hikari.Embed(
            title="🥐 Bakery Shift Complete 🥐",
            description=splash_text,
            color=embed_colour
        )
    )
    if not failed:
        embed.add_field(
            name="Card Obtained!",
            value="While cleaning up the bakery, you discovered a new card."
        )
    embed.set_image(image)

    await ctx.respond(embed)


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)

def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(plugin)
