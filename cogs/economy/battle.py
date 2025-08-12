from library.database import economy, dbcards
from cogs.economy.pokemon_group import group
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
    length=86400, # 1 Day
    bucket=lightbulb.buckets.UserBucket,
    uses=1
)
@lightbulb.command(name='battle', description="Earn some FumaCoins and a card!")
@lightbulb.implements(lightbulb.SlashSubCommand)
@dc.prechecks()
async def bot_command(ctx: lightbulb.SlashContext):
    user_account = economy.account(ctx.author.id)
    money_gained = random.randint(10, 150)
    failed = random.randint(1, 100) == 50

    splash_text = "You earned some PokeCoins!"
    if not failed:
        splash_randomizer = random.randint(1, 3)
        if money_gained == 10:
            if splash_randomizer == 1:
                splash_text = "You fought hard, fumbling around cluelessly and won on pure dumb luck, earnt 10 FumaCoins."
            elif splash_randomizer == 2:
                splash_text = "You sent out your pokemon and it immediately tripped over its tail and died on the spot. Your opponent gave you 10 FumaCoins out of pity."
            elif splash_randomizer == 3:
                splash_text = "You tried to send out your pokemon but accidentally hit the back of your head and knocked some FumaCoins out of your hat and got 10 coins!"
        elif money_gained > 10 and money_gained <= 30:
            if splash_randomizer == 1:
                splash_text = f"You fought hard, and lost! but your opponent gave you {money_gained} FumaCoins out of a mild respect for your skill."
            elif splash_randomizer == 2:
                splash_text = (f"You almost lost the battle, but at the last moment, "
                               f"your opponent's pokemon tripped over, "
                               f"giving you a chance for the needed, "
                               f"solid blow. You won {money_gained} FumaCoins!")
            elif splash_randomizer == 3:
                splash_text = f"You both put a bet on who'd win a fight, and your opponents pokemon refused to fight! They had to give you {money_gained} FumaCoins by default."
        elif money_gained > 30 and money_gained <= 60:
            if splash_randomizer == 1:
                splash_text = f"You fought well, and won! Your opponent gave you a good fight, and the opponent gave you {money_gained} FumaCoins for your skill."
            elif splash_randomizer == 2:
                splash_text = f"You lured your opponent into a trap during a fight, and won the fight bet, earning you {money_gained} FumaCoins!"
            elif splash_randomizer == 3:
                splash_text = (f"You stared awkwardly at your opponent's pokemon uncomfortably for a while, "
                               f"and it gave up out of social anxiety. You stole {money_gained} FumaCoins from its wallet.")
        elif money_gained > 60 and money_gained < 100:
            if splash_randomizer == 1:
                splash_text = (f"You fought a fair and honest battle, and your opponent lost. "
                               f"They were so amazed by your battle honor, that they gave you {money_gained} FumaCoins for it!")
            elif splash_randomizer == 2:
                splash_text = ("You were fighting when you realized a weakness in your opponent's pokemon, and exploited it. "
                               f"They commended you for your keen observation and gave you {money_gained} FumaCoins.")
            elif splash_randomizer == 3:
                splash_text = (f"You had a good time fighting and laughed with your opponent, they far outmatched you however and you lost. "
                               f"They gave you {money_gained} FumaCoins because they really liked you!")
        elif money_gained >= 100 and money_gained < 150:
            if splash_randomizer == 1:
                splash_text = ("You glared at your opponents pokemon like the Gigachad you are, "
                               f"and it decided not to oppose you out of respect, and gave you {money_gained} FumaCoins for your respectableness.")
            elif splash_randomizer == 2:
                splash_text = ("You commanded your pokemon in its fight with a strong smile and pure efficiency, arms crossed, and won. "
                               f"Your opponent paid you {money_gained} FumaCoins for existing and saluted you.")
            elif splash_randomizer == 3:
                splash_text = ("You fought hard against a thief with 3 pokemon with your single pokemon. "
                               "After the smoke cleared, it was obvious you were victorious. "
                               f"They gave you {money_gained} FumaCoins to persuade you to not call the cops.")
        elif money_gained == 150:
            if splash_randomizer == 1:
                splash_text = ("You stood forth, and crossed your arms without sending out a pokemon to oppose the opposer.\n"
                               f"It shuddered, and gave up immediately and gave you {money_gained} in propitiation for their salvation.")
            elif splash_randomizer == 2:
                splash_text = ("You stood forth to oppose the opposer, and almost hammered your opponent into the ground, but stopped right before the impact. "
                               f"Your opponent, seeing it was no match, gave up and gave you {money_gained} FumaCoins out of propitiation.")
            elif splash_randomizer == 3:
                splash_text = ("You looked at your opponent before the battle had even thought to begin, and they walked away. The concept of the battle also walked away. "
                               "The next day, your opponent woke up with a black eye and horrible nightmares of opposing you."
                               f"They desperately fund raised {money_gained} FumaCoins and gave it to you out of fear.")
        else:
            splash_text = "SPLASH_TEXT_ERROR"

        user_account.fumacoins.modify_balance(money_gained, operator="+")
    else:
        splash_text = ("You threw a rat at Arceus (God of Gods) and barely got away with it, and only because it let you. "
                       f"You had to offer {money_gained // 2} FumaCoins to its shrine for its forgiveness.")
        user_account.fumacoins.modify_balance(money_gained // 2, operator="-")

    if money_gained >= 40:
        embed_colour = 0x00ff00
    else:
        embed_colour = 0x0000ff
    if failed:
        embed_colour = 0xff0000

    obtained_card = dbcards.pull_random_card()
    img_bytes = dbcards.load_img_bytes(obtained_card['identifier'])

    if obtained_card['rarity'] >= 3:
        embed_colour = 0x00ff00
    elif obtained_card['tier'] > 1:
        embed_colour = 0x00ff00

    image = hikari.Bytes(img_bytes, f"{obtained_card['name']}.png")

    embed = (
        hikari.Embed(
            title="⚔️ Battle Result ⚔️",
            description=splash_text,
            color=embed_colour,
        )
        .add_field(
            "Card Obtained!",
            "At the end of the fight, you found a new card in your pokedex."
        )
        .set_image(image)
    )

    await ctx.respond(embed)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
