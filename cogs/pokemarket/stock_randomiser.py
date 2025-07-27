from library.database import pokemarket
from library.botapp import tasks
import lightbulb

plugin = lightbulb.Plugin(__name__)

@tasks.task(h=6, wait_before_execution=False, auto_start=True)
async def pokemarket_stock_randomiser():
    pokemarket.randomise_stock()

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)
