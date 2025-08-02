from library.botapp import botapp
import sqlite3
import logging

# Import all the extra DB Classes here, so there's a global place to import them from.
# noinspection PyUnresolvedReferences
from library.dbmodules import dbuser, stdn_events, lmtd_events, dbcards, eventlogs, economy, pokemarket, nichoshop
# noinspection PyUnresolvedReferences
from library.dbmodules.shared import *

DB_PATH = botapp.d['DB_PATH']

class database:
    @staticmethod
    def modernize():
        """
        This function is used to modernise the database to the current version. It will check if the tables exist, and
        if they don't, it will create them. If the tables do exist, it will check if the columns are up to date, and if
        they aren't, it will update them.

        :return:
        """
        # Function I pulled from another project.
        # Using this dict, it formats the SQL query to create the tables if they don't exist
        table_dict = {
            'inventories': {
                'inventory_id': "INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT",
                'item_identifier': 'TEXT NOT NULL',
                'item_name': 'INTEGER NOT NULL',
                'user_id': 'INTEGER NOT NULL',
                'amount': 'INTEGER NOT NULL DEFAULT 0',
            },
            'global_cards': {
                "identifier": "TEXT NOT NULL PRIMARY KEY",
                'name': 'TEXT NOT NULL',
                'description': 'TEXT NOT NULL',
                'rarity': 'INTEGER NOT NULL DEFAULT 1',
                'card_tier': 'INTEGER NOT NULL DEFAULT 1',  # Standard is 1. Event is 2. Limited is 3
                'img_bytes': 'BLOB',
                'pullable': 'BOOLEAN NOT NULL DEFAULT TRUE',
                'card_group': 'TEXT NOT NULL DEFAULT "None"',
            },
            'banned_users': {
                "user_id": "INTEGER NOT NULL PRIMARY KEY",
                "ban_status": "BOOLEAN NOT NULL DEFAULT FALSE",
                "reason": "TEXT NOT NULL"
            },
            'stdn_events': {
                "name": "TEXT NOT NULL PRIMARY KEY",
                "schedulable": "BOOLEAN NOT NULL DEFAULT True",
                "onetime": "BOOLEAN NOT NULL DEFAULT False",
            },
            'stdn_events_schedule': {
                "entry_id": "INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT",
                "event_name": "TEXT NOT NULL",
                "start_time": "DATETIME NOT NULL",
                "end_time": "DATETIME NOT NULL",
            },
            'stdn_event_cards': {
                "entry_id": "INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT",
                "event_name": "TEXT NOT NULL",
                "card_identifier": "TEXT NOT NULL",
            },
            'limited_events': {
                "name": "TEXT NOT NULL PRIMARY KEY",
                "schedulable": "BOOLEAN NOT NULL DEFAULT True",
            },
            'limited_events_schedule': {
                "entry_id": "INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT",
                "event_name": "TEXT NOT NULL",
                "start_time": "DATETIME NOT NULL",
                "end_time": "DATETIME NOT NULL",
            },
            'limited_event_cards': {
                "entry_id": "INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT",
                "event_name": "TEXT NOT NULL",
                "card_identifier": "TEXT NOT NULL",
            },
            'economy_bank': {
                "user_id": "INTEGER NOT NULL PRIMARY KEY",
                "pk_balance": "INTEGER NOT NULL DEFAULT 0",
                "nk_balance": "INTEGER NOT NULL DEFAULT 0",
            },
            'nicho_market_stock': {
                'seller_id': 'INTEGER NOT NULL PRIMARY KEY',
                'card_id': 'TEXT NOT NULL',
                'amount': 'INTEGER NOT NULL',
                'price': 'INTEGER NOT NULL',
                'time_added': 'DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP',
            },
            'pokeshop_stock': {
                'item_id': 'TEXT NOT NULL PRIMARY KEY',
                'price': 'INTEGER NOT NULL',
                'item_type': 'INTEGER NOT NULL',  # 0 = Variety pack, 1 = Random pack.
                'amount': 'INTEGER NOT NULL',  # How many cards you get from the pack
                'filter_arg': 'TEXT NOT NULL DEFAULT "<pullable=true><card_tier=1>"',
            }
        }

        for table_name, columns in table_dict.items():
            with sqlite3.connect(DB_PATH) as conn:
                cur = conn.cursor()
                cur.execute(f'''
                        SELECT name
                        FROM sqlite_master
                        WHERE type='table' AND name='{table_name}';
                    ''')
                table_exist = cur.fetchone() is not None

            # If the table exists, check and update columns
            if table_exist:
                for column_name, column_properties in columns.items():
                    # Check if the column exists
                    cur.execute(f'''
                            PRAGMA table_info({table_name});
                        ''')
                    columns_info = cur.fetchall()
                    column_exist = any(column_info[1] == column_name for column_info in columns_info)

                    # If the column doesn't exist, add it
                    if not column_exist:
                        try:
                            cur.execute(f'ALTER TABLE {table_name} ADD COLUMN {column_name} {column_properties};')
                        except sqlite3.OperationalError as err:
                            print(f"ERROR EDITING TABLE {table_name}, ADDING COLUMN {column_name} {column_properties}")
                            raise err

            # If the table doesn't exist, create it with columns
            else:
                columns_str = ', '.join(
                    [f'{column_name} {column_properties}' for column_name, column_properties in columns.items()]
                )
                try:
                    cur.execute(f'CREATE TABLE {table_name} ({columns_str});')
                except sqlite3.OperationalError as err:
                    print(f"There was a problem creating the table {table_name} with columns {columns_str}")
                    logging.error(f"An error occurred while creating the table {table_name} with columns {columns_str}", err)
                    exit(1)
