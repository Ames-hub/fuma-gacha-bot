from cogs.economy.bakery_group import group
from library.database import economy
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
@lightbulb.command(name='advertise', description="Advertise the bakery for a good payday!", pass_options=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
@dc.prechecks('advertise', cooldown_s=1800)  # 30 minutes
async def bot_command(ctx: lightbulb.SlashContext):
    target_acc = economy.account(ctx.author.id)

    flavour_text = random.choice([
        "Your sign spins around directing crowds to the bakery, neat!",
        "You've been yelling out about free samples for a while now.",
        "The discord invite link, you keep thinking who you could share it to.",
        "The discord invite link, you keep thinking who you could share it to 👀 (right? just saying! It'd help a lot!)"
        "The smell of fresh bread keeps you going.",
        "Someone comes up and asks you what you're advertising, that's your queue!",
        "You consider world domination as your sign advertises the bakery."
    ])

    payout = random.randint(200, 500)

    embed = (
        hikari.Embed(
            title="Come look!",
            description=f"You advertised the bakery! {flavour_text}",
            colour=ctx.bot.d['branding']['embed']
        )
        .add_field(
            name="Payout!",
            value=f"You got {payout} {ctx.bot.d['coin_name']['normal']}s!"
        )
    )

    target_acc.normalcoin.modify_balance(payout, "+")

    await ctx.respond(embed)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
