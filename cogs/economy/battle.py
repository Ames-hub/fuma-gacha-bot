from library.database import economy, dbcards
from cogs.economy.pokemon_group import group
from library import decorators as dc
import lightbulb
import hikari
import random

plugin = lightbulb.Plugin(__name__)

# -----------------------------
# Splash text configuration
# -----------------------------

BATTLE_SPLASHES = [
    {
        "min": 1000,
        "max": 1000,
        "texts": [
            "You fought hard, fumbling around cluelessly and won on pure dumb luck, earning 10 FumaCoins.",
            "You sent out your Pokémon and it immediately tripped over its tail and died. Your opponent gave you 10 FumaCoins out of pity.",
            "You tried to send out your Pokémon but hit the back of your head and knocked 10 FumaCoins out of your hat."
        ]
    },
    {
        "min": 1101,
        "max": 1200,
        "texts": [
            "You fought hard and lost, but your opponent respected your skill and gave you {coins} FumaCoins.",
            "Your opponent’s Pokémon tripped at the last second. You seized the moment and won {coins} FumaCoins.",
            "You both placed a bet, but your opponent’s Pokémon refused to fight. You won {coins} FumaCoins by default."
        ]
    },
    {
        "min": 1201,
        "max": 1300,
        "texts": [
            "You fought well and won. Your opponent rewarded your skill with {coins} FumaCoins.",
            "You lured your opponent into a trap and won the fight bet, earning {coins} FumaCoins.",
            "You stared so awkwardly that the opposing Pokémon quit out of social anxiety. You stole {coins} FumaCoins."
        ]
    },
    {
        "min": 1301,
        "max": 1399,
        "texts": [
            "You fought an honorable battle and were rewarded {coins} FumaCoins.",
            "You exploited a weakness mid-fight. Your opponent admired the insight and paid you {coins} FumaCoins.",
            "You lost the fight, but your opponent liked you enough to give you {coins} FumaCoins anyway."
        ]
    },
    {
        "min": 1400,
        "max": 1499,
        "texts": [
            "You glared at your opponent like a Gigachad. They surrendered and paid you {coins} FumaCoins.",
            "You commanded your Pokémon flawlessly. Your opponent saluted and paid {coins} FumaCoins.",
            "You defeated a thief and their three Pokémon. They paid you {coins} FumaCoins to keep quiet."
        ]
    },
    {
        "min": 1500,
        "max": 1500,
        "texts": [
            "You crossed your arms. The battle surrendered itself and paid you {coins} FumaCoins.",
            "You nearly obliterated your opponent but stopped short. They paid you {coins} FumaCoins in fear.",
            "The idea of battling you fled. Your opponent fundraised {coins} FumaCoins out of sheer terror."
        ]
    }
]


def get_battle_splash(coins: int) -> str:
    for tier in BATTLE_SPLASHES:
        if tier["min"] <= coins <= tier["max"]:
            return random.choice(tier["texts"]).format(coins=coins)
    return "You fought bravely and earned your reward."


# -----------------------------
# Command
# -----------------------------

@group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.command(
    name="battle",
    description="Earn some FumaCoins and a card!"
)
@lightbulb.implements(lightbulb.SlashSubCommand)
@dc.prechecks("economy battle", cooldown_s=86400)
async def bot_command(ctx: lightbulb.SlashContext):
    user_account = economy.account(ctx.author.id)

    money_gained = random.randint(1000, 1500)
    failed = random.random() < 0.01  # 1% failure chance

    if failed:
        loss = money_gained // 2
        splash_text = (
            "You threw a rat at Arceus and barely escaped. "
            f"You offered {loss} FumaCoins at its shrine for forgiveness."
        )
        user_account.fumacoins.modify_balance(loss, operator="-")
        embed_colour = 0xFF0000
    else:
        splash_text = get_battle_splash(money_gained)
        user_account.fumacoins.modify_balance(money_gained, operator="+")
        embed_colour = 0x00FF00

    # -----------------------------
    # Card reward
    # -----------------------------

    obtained_card = dbcards.pull_random_card()
    img_bytes = dbcards.load_img_bytes(obtained_card["identifier"])

    if obtained_card["rarity"] >= 3 or obtained_card["tier"] > 1:
        embed_colour = 0x00FF00

    image = hikari.Bytes(img_bytes, f"{obtained_card['name']}.png")

    embed = (
        hikari.Embed(
            title="⚔️ Battle Result ⚔️",
            description=splash_text,
            color=embed_colour
        )
        .add_field(
            name="Card Obtained!",
            value="At the end of the fight, you found a new card in your Pokédex."
        )
        .set_image(image)
    )

    await ctx.respond(embed)


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(plugin)
