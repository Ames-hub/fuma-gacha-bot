from library.database import database
from library.botapp import botapp

# Keep DB Up to date
database.modernize()

# Load all extensions
botapp.load_extensions_from("cogs/card_group")
botapp.load_extensions_from("cogs/other")

botapp.run()