from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from library.database import database
from library.botapp import botapp
from cryptography import x509
import datetime
import uvicorn
import asyncio
import os

# Keep DB Up to date
database.modernize()

# Load all extensions
botapp.load_extensions_from("cogs/card_group")
botapp.load_extensions_from("cogs/bakesale")
botapp.load_extensions_from("cogs/donutshop")
botapp.load_extensions_from("cogs/economy")
botapp.load_extensions_from("cogs/staff")
botapp.load_extensions_from("cogs/staff/events")
botapp.load_extensions_from("cogs/staff/limited_events")
botapp.load_extensions_from("cogs/staff/botlogging")
botapp.load_extensions_from("cogs/other")
botapp.load_extensions_from("cogs/notifs")
botapp.load_extensions_from("cogs/botworkers")

botapp.d['maintainer'] = 913574723475083274
botapp.d['admin_ids'] = [
    913574723475083274,
    299709812848197644,
    690236383410782301,
    340243618101198858,
    740312826253410355
]
botapp.d['admin_roles'] = [
    1386187466897227890, # Admin role
    1386535298346782761, # Center staff Role
]

DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
botapp.d['DEBUG'] = DEBUG

botapp.d['coin_name'] = {}
botapp.d['coin_name']['normal'] = "DonutCoin"  # "Normal" Coin name. Used in pokeshop.
botapp.d['coin_name']['better'] = "Woonagi Point"  # Used in bakesale

# Init Cache dicts
botapp.d['inventory_username_cache'] = {}
botapp.d['event_checked_cache'] = {}
botapp.d['limited_event_checked_cache'] = {}

botapp.d['pokestore'] = {
    'user_cache': {}
}

botapp.d['rarity_emojis_text'] = {
    1: "<:agathedonut:1454905529016123474>",
    2: "<:agathedonut:1454905529016123474>" * 2,
    3: "<:agathedonut:1454905529016123474>" * 3,
    4: "<:agathedonut:1454905529016123474>" * 4,
    5: "<:agathedonut:1454905529016123474>" * 5,
}

botapp.d['bakesale'] = {
    "cache": {
        "page_list": [],
        "last_update": datetime.datetime.now() - datetime.timedelta(seconds=30),
    },
    "open": True
}

botapp.d['config'] = {  # The default config
    "event_channel": {
        "id": None,
    },
}

botapp.d['cooldowns'] = {}

botapp.d['packtypes'] = {
    'random': 0,
    'choice': 1,
}

botapp.d['card_tier_names'] = {
    "numeric": {
        1: "Standard",
        2: "Event",
        3: "Limited",
    },
    "text": {
        "Standard": 1,
        "Event": 2,
        "Limited": 3
    }
}

botapp.d['cooldowns_on'] = True

ssl_keyfile_dir = "certs/key.pem"
ssl_certfile_dir = "certs/cert.pem"

def generate_self_signed_cert(country_name, province_name, locality_name, organisation_name, common_name="localhost", valid_days=365):
    if os.path.exists(ssl_keyfile_dir) or os.path.exists(ssl_certfile_dir):
        os.remove('certs')
        os.makedirs('certs')

    # Generate private key
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # Generate a self-signed certificate
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"{}".format(country_name)),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"{}".format(province_name)),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"{}".format(locality_name)),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"{}".format(organisation_name)),
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
    ])

    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.now(datetime.timezone.utc)
    ).not_valid_after(
        datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=valid_days)
    ).add_extension(
        x509.SubjectAlternativeName([x509.DNSName(common_name)]),
        critical=False,
    ).sign(key, hashes.SHA256())

    # Write private key to file
    with open(ssl_keyfile_dir, "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    # Write certificate to file
    with open(ssl_certfile_dir, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    print(f"Self-signed certificate saved to {ssl_certfile_dir}")
    print(f"Private key saved to {ssl_keyfile_dir}")
    return True

from webpanel.library.auth import authbook

async def main():
    if not os.path.exists(ssl_keyfile_dir) or not os.path.exists(ssl_certfile_dir):
        print("SSL Certificate or Key not found, generating self-signed certificate...")
        country_code = input("Enter Country Code (2 letter code, e.g., US): ") or "AU"
        state_name = input("Enter State or Province Name: ") or "Western Australia"
        locality_name = input("Enter Locality or City Name: ") or "Perth"
        common_name = input("Enter Common Name (e.g., localhost or your domain): ") or "localhost"

        success = generate_self_signed_cert(
            country_name=country_code,
            province_name=state_name,
            locality_name=locality_name,
            organisation_name="Gacha Bot Devs",
            common_name=common_name,
            valid_days=999
        )
        if success:
            print("Self-signed certificate generated successfully.")
        else:
            print("Failed to generate self-signed certificate. Exiting.")
            return
        
    account_count = len(authbook.list_accounts())
    if account_count == 0:
        print("Please create an admin account for the web panel to continue.")
        while True:
            username = input("Enter admin username: ").strip()
            password = input("Enter admin password: ").strip()
            try:
                authbook.create_account(username, password, is_admin=True)
                print(f"Admin account '{username}' created successfully.")
                break
            except Exception as e:
                print(f"Error creating account: {e}. Please try again.")

    config = uvicorn.Config(
        "webpanel.webpanel:fastapi",
        host="0.0.0.0" if not DEBUG else "127.0.0.1",
        port=8010,
        loop="asyncio",
        lifespan="on",
        reload=False,  # <- important
        ssl_certfile=ssl_certfile_dir,
        ssl_keyfile=ssl_keyfile_dir
    )
    server = uvicorn.Server(config)

    await asyncio.gather(
        server.serve(),
        botapp.start(shard_count=1)
    )

bot_only = False

if __name__ == "__main__":
    if bot_only:
        try:
            botapp.run()
        except KeyboardInterrupt:
            print("Ending process.")
    else:
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            print("Ending processes.")