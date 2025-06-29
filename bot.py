from library.database import database
from library.botapp import botapp
import os

# Keep DB Up to date
database.modernize()

# Load all extensions
botapp.load_extensions_from("cogs/card_group")
botapp.load_extensions_from("cogs/staff")
botapp.load_extensions_from("cogs/other")

botapp.d['maintainer'] = 913574723475083274
botapp.d['admin_roles'] = [1386536393085419664, 1386536159185862768]

DEBUG = os.environ.get("DEBUG").lower() == "true"
botapp.d['DEBUG'] = DEBUG

botapp.run(shard_count=5 if not DEBUG else 1)