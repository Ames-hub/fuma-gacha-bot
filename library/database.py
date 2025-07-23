from library.botapp import botapp
import datetime
import sqlite3
import logging
import secrets
import hikari
import json
import io

DB_PATH = 'botapp.sqlite'

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
            },
            'banned_users': {
                "user_id": "INTEGER NOT NULL PRIMARY KEY",
                "ban_status": "BOOLEAN NOT NULL DEFAULT FALSE",
                "reason": "TEXT NOT NULL"
            },
            'stdn_events': {
                "name": "TEXT NOT NULL PRIMARY KEY",
                "onetime": "BOOLEAN NOT NULL DEFAULT FALSE",
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

class dbuser:
    @staticmethod
    def set_user_ban(ban_status:bool, user_id:int, reason:str="No reason provided."):
        conn = sqlite3.connect(DB_PATH)
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO banned_users (user_id, ban_status, reason)
                VALUES (?, ?, ?)
                ON CONFLICT (user_id) DO UPDATE SET ban_status = ?, reason = ?
                """,
                (user_id, ban_status, reason, ban_status, reason),
            )
            conn.commit()
            return True
        except sqlite3.OperationalError:
            conn.rollback()
            return False
        finally:
            conn.close()

    @staticmethod
    def has_admin_role(user_role_ids):
        admin_roles = botapp.d['admin_roles']
        for role_id in user_role_ids:
            for admin_role_id in admin_roles:
                if role_id == admin_role_id:
                    return True
        return False

    @staticmethod
    def run_ban_check(user_id: int):
        conn = sqlite3.connect(DB_PATH)
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT ban_status, reason FROM banned_users WHERE user_id = ?
                """,
                (user_id,),
            )
            data = cur.fetchone()
            banned = bool(data[0]) if data else False
            return banned
        except sqlite3.OperationalError:
            conn.rollback()
            return False
        finally:
            conn.close()

    @staticmethod
    def get_inventory(user_id, search_for=None):
        conn = sqlite3.connect(DB_PATH)

        try:
            cursor = conn.cursor()
            if search_for is None:
                cursor.execute(
                    """
                    SELECT item_name, item_identifier, amount FROM inventories WHERE user_id = ?
                    """,
                    (user_id,)
                )
            else:
                search_is_id = " " not in search_for and search_for.lower().startswith("id:")
                if search_is_id:
                    search_for = search_for.replace("id:", "")

                cursor.execute(
                    f"""
                    SELECT item_name, item_identifier, amount
                    FROM inventories
                    WHERE user_id = ?
                    AND {"item_name" if not search_is_id else "item_identifier"} = ?
                    """,
                    (user_id, search_for,)
                )
            data = cursor.fetchall()

            inventory = {}
            for row in data:
                inventory[row[1]] = {
                    "name": row[0],
                    "identifier": row[1],
                    "amount": row[2],
                }

            return inventory
        except sqlite3.OperationalError as err:
            conn.rollback()
            logging.error(f"An error occurred while running a command: {err}", exc_info=err)
        finally:
            conn.close()

class dbcards:
    class NonexistantCard(Exception):
        def __init__(self):
            pass

        def __str__(self):
            return "Nonexistant card."

    @staticmethod
    def set_pullability(card_id:str, value:bool):
        with sqlite3.connect(DB_PATH) as conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    """
                    UPDATE global_cards SET pullable = ? WHERE identifier = ?
                    """,
                    (value, card_id)
                )
                conn.commit()
                return True
            except sqlite3.OperationalError:
                conn.rollback()
                return False

    @staticmethod
    def check_exists(card_id: int):
        with sqlite3.connect(DB_PATH) as conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    """
                    SELECT EXISTS(SELECT 1 FROM global_cards WHERE identifier = ?);
                    """,
                    (card_id,)
                )
                return cur.fetchone()[0]
            except sqlite3.OperationalError:
                conn.rollback()
                return False

    @staticmethod
    def get_tier(card_id: int, as_number=False):
        if dbcards.check_exists(card_id) is False:
            raise dbcards.NonexistantCard()

        with sqlite3.connect(DB_PATH) as conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    """
                    SELECT card_tier FROM global_cards WHERE identifier = ?;
                    """,
                    (card_id,)
                )
                if as_number:
                    return cur.fetchone()[0]
                else:
                    return {1: "Standard", 2: "Event", 3: "Limited"}[cur.fetchone()[0]]
            except sqlite3.OperationalError:
                conn.rollback()
                return False

    @staticmethod
    def spawn_card(card_id: str, amount: int, user_id: int):
        if amount < 1:
            return False

        conn = sqlite3.connect(DB_PATH)
        try:
            cur = conn.cursor()

            card_id = card_id.replace("id:", "")

            # Step 1: Get the item details from global_cards
            cur.execute(f"""
                SELECT identifier, name FROM global_cards
                WHERE identifier = ? AND card_tier IS NOT 3
            """, (card_id,))

            card_data = cur.fetchone()

            if not card_data:
                return False

            item_identifier, item_name = card_data

            # Step 2: Check if the user already has it
            cur.execute("""
                SELECT amount FROM inventories
                WHERE user_id = ? AND item_identifier = ?
            """, (user_id, item_identifier))

            existing = cur.fetchone()
            if existing:
                cur.execute("""
                    UPDATE inventories
                    SET amount = amount + ?
                    WHERE user_id = ? AND item_identifier = ?
                """, (amount, user_id, item_identifier))
            else:
                cur.execute("""
                    INSERT INTO inventories (item_identifier, item_name, user_id, amount)
                    VALUES (?, ?, ?, ?)
                """, (item_identifier, item_name, user_id, amount))

            conn.commit()
            return True

        except sqlite3.OperationalError:
            conn.rollback()
            return False
        finally:
            conn.close()

    @staticmethod
    def add_card(card_id, name, description, rarity, card_tier, img_bytes, pullable:bool):
        conn = sqlite3.connect(DB_PATH)

        assert card_tier in [1, 2, 3], "Card tier must be 1, 2, or 3. (1, Standard. 2, Event. 3, Limited)"
        assert type(name) is str, "Name must be a string."
        assert type(description) is str, "Description must be a string."
        assert type(rarity) is int, "Rarity must be an integer from 1 to 5."

        if card_id is not None:
            if type(card_id) is not str:
                return {'success': False, 'card_id': None, 'error': 'Card ID must be a string.'}
            elif " " in card_id:
                return {'success': False, 'card_id': None, 'error': 'Card ID cannot contain spaces.'}

        try:
            if card_id is None:
                card_id = secrets.token_urlsafe(6)
            cur = conn.cursor()
            cur.execute(
                f"""
                INSERT INTO global_cards (identifier, name, description, rarity, img_bytes, pullable)
                VALUES (?, ?, ?, ?, ?, ?)
                {"RETURNING global_cards.identifier" if card_id is None else ""}
                """,
                (card_id, str(name), str(description), int(rarity), img_bytes, bool(pullable)),
            )
            conn.commit()
            if card_id is None:
                return {'success': True, 'card_id': cur.fetchone()[0]}
            return {'success': True, 'card_id': card_id}
        except sqlite3.OperationalError as err:
            logging.error(err, exc_info=err)
            conn.rollback()
            return {'success': False, 'card_id': None, "error": "Critical Database Error."}
        finally:
            conn.close()

    @staticmethod
    def rm_card(card_id):
        conn = sqlite3.connect(DB_PATH)
        try:
            cur = conn.cursor()
            cur.execute(
                """
                DELETE FROM global_cards WHERE identifier = ?
                """,
                (card_id,),
            )
            conn.commit()
            return True
        except sqlite3.OperationalError as err:
            logging.error(err, exc_info=err)
            conn.rollback()
            return False
        finally:
            conn.close()

    @staticmethod
    def gift_card(cardname: str, giving_amount: int, giver_id: int, receiver_id: int):
        if giving_amount < 1:
            return "Amount must be at least 1."

        is_id = " " not in cardname and cardname.lower().startswith("id:")
        if is_id:
            cardname = cardname.replace("id:", "")

        conn = sqlite3.connect(DB_PATH)
        try:
            cur = conn.cursor()

            # Step 1: Fetch item from the giver
            cur.execute(f"""
                SELECT item_identifier, item_name, amount FROM inventories
                WHERE user_id = ? AND {'item_identifier' if is_id else 'item_name'} = ?
            """, (giver_id, cardname))

            item = cur.fetchone()
            if not item:
                return "Giver doesn't own the item."

            item_identifier, item_name, giver_amount = item

            if giver_amount < giving_amount:
                return f"Not enough quantity to give. You have {giver_amount}."

            # Step 2: Deduct from giver
            if giver_amount == giving_amount:
                cur.execute("""
                    DELETE FROM inventories
                    WHERE user_id = ? AND item_identifier = ?
                """, (giver_id, item_identifier))
            else:
                cur.execute("""
                    UPDATE inventories
                    SET amount = amount - ?
                    WHERE user_id = ? AND item_identifier = ?
                """, (giving_amount, giver_id, item_identifier))

            # Step 3: Add to receiver
            cur.execute("""
                SELECT amount FROM inventories
                WHERE user_id = ? AND item_identifier = ?
            """, (receiver_id, item_identifier))

            receiver_item = cur.fetchone()
            if receiver_item:
                cur.execute("""
                    UPDATE inventories
                    SET amount = amount + ?
                    WHERE user_id = ? AND item_identifier = ?
                """, (giving_amount, receiver_id, item_identifier))
            else:
                cur.execute("""
                    INSERT INTO inventories (item_identifier, item_name, user_id, amount)
                    VALUES (?, ?, ?, ?)
                """, (item_identifier, item_name, receiver_id, giving_amount))

            conn.commit()
            return "Transfer successful."

        except sqlite3.OperationalError as err:
            conn.rollback()
            return f"Database error: {err}"
        finally:
            conn.close()

    @staticmethod
    def view_card(name:str):
        conn = sqlite3.connect(DB_PATH)

        # TODO: Reimplement viewing card by name. For now, we enforce "is id"
        is_id = True
        #        is_id = " " not in name and name.lower().startswith("id:")
        #        if is_id:
        #            name = name.replace("id:", "")

        try:
            cur = conn.cursor()
            cur.execute(
                f"""
                SELECT identifier, name, description, rarity, img_bytes, card_tier, pullable
                FROM global_cards
                WHERE {'name' if not is_id else 'identifier'} = ?
                """,
                (name,),
            )
            data = cur.fetchall()
            conn.close()
            if data is None:
                return [{}]
            elif len(data) == 0:
                return [{}]
            elif len(data) > 1:
                parsed_data = []
                for item in data:
                    parsed_data.append({
                        'identifier': item[0],
                        'name': item[1],
                        'description': item[2],
                        'rarity': item[3],
                        'img_bytes': item[4],
                        'tier': item[5],
                        'pullable': bool(item[6]),
                    })
                return parsed_data
            else:
                data = data[0]
                return [{
                    'identifier': data[0],
                    'name': data[1],
                    'description': data[2],
                    'rarity': data[3],
                    'img_bytes': data[4],
                    'tier': data[5],
                    'pullable': bool(data[6]),
                }]
        except sqlite3.OperationalError:
            conn.rollback()
            conn.close()
            return False

    @staticmethod
    def load_img_bytes(card_id):
        conn = sqlite3.connect(DB_PATH)
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT img_bytes FROM global_cards WHERE identifier = ?
                """,
                (card_id,),
            )

            data = cur.fetchone()
            conn.close()
            if data is None:
                raise ValueError("Image bytes data cannot be None.")
            else:
                return io.BytesIO(data[0])
        except sqlite3.OperationalError as err:
            conn.rollback()
            conn.close()
            raise err

    @staticmethod
    def save_to_invent(user_id, item_identifier, item_name):
        conn = sqlite3.connect(DB_PATH)
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT amount FROM inventories
                WHERE user_id = ? AND item_identifier = ?
                """,
                (user_id, item_identifier)
            )
            data = cursor.fetchone()

            if data is None:
                cursor.execute(
                    """
                    INSERT INTO inventories (item_identifier, item_name, user_id, amount)
                    VALUES (?, ?, ?, 1)
                    """,
                    (item_identifier, item_name, user_id)
                )
            else:
                cursor.execute(
                    """
                    UPDATE inventories
                    SET amount = amount + 1
                    WHERE user_id = ? AND item_identifier = ?
                    """,
                    (user_id, item_identifier)
                )

            conn.commit()
        except sqlite3.OperationalError as e:
            conn.rollback()
            logging.error("Database error in save_to_invent: %s", e)
        finally:
            conn.close()

    @staticmethod
    def pull_random_card(exception_names=None):
        if exception_names is None:
            exception_names = []

        conn = sqlite3.connect(DB_PATH)
        try:
            cursor = conn.cursor()

            base_query = '''
        SELECT identifier, name, description, rarity FROM global_cards WHERE pullable = True
        '''

            where_clause = ''
            if exception_names:
                placeholders = ','.join('?' for _ in exception_names)
                where_clause = f'WHERE identifier NOT IN ({placeholders})'

            full_query = f'''
        {base_query}
        {where_clause}
        ORDER BY
            CASE rarity
                WHEN 1 THEN ABS(RANDOM()) * 1.0
                WHEN 2 THEN ABS(RANDOM()) * 1.25
                WHEN 3 THEN ABS(RANDOM()) * 1.67
                WHEN 4 THEN ABS(RANDOM()) * 5.0
                WHEN 5 THEN ABS(RANDOM()) * 8.0
                ELSE ABS(RANDOM()) * 10.0
            END
        LIMIT 1
        '''

            cursor.execute(full_query, exception_names)
            data = cursor.fetchone()
            if not data:
                return False
            else:
                return {
                    "identifier": data[0],
                    "name": data[1],
                    "description": data[2],
                    "rarity": data[3],
                }

        except sqlite3.OperationalError as err:
            logging.error(err)
        finally:
            conn.close()

class pokemarket:
    """
    TODO Item. Need further information from head designer.
    This feature is currently undecided as to the nature of what it does.
    """
    pass

class events:
    class TimeError(Exception):
        def __init__(self):
            pass

        def __str__(self):
            return "Invalid time format."

    class EventExistingError(Exception):
        def __init__(self):
            pass

        def __str__(self):
            return "Event already exists and cannot be created again."

    class EventSchedulingError(Exception):
        def __init__(self):
            pass

        def __str__(self):
            return "Event scheduling failed."

    class EventCardAssosciationError(Exception):
        def __init__(self):
            pass

        def __str__(self):
            return "Event card assosciation failed."

    @staticmethod
    def delete_schedule(entry_id):
        with sqlite3.connect(DB_PATH) as conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    """
                    DELETE FROM stdn_events_schedule WHERE entry_id = ?
                    """,
                    (entry_id,),
                )
                conn.commit()
                return True
            except sqlite3.OperationalError:
                conn.rollback()
                return False

    @staticmethod
    def get_all_events():
        with sqlite3.connect(DB_PATH) as conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    """
                    SELECT name FROM stdn_events
                    """
                )
                data = cur.fetchall()
                parsed_data = []
                for item in data:
                    parsed_data.append(item[0])
                return parsed_data
            except sqlite3.OperationalError:
                conn.rollback()
                return False

    @staticmethod
    def get_event_schedule(event_name):
        with sqlite3.connect(DB_PATH) as conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    """
                    SELECT start_time, end_time, entry_id FROM stdn_events_schedule WHERE event_name = ?
                    """,
                    (event_name,),
                )
                data = cur.fetchall()
                if not data:
                    return None
                else:
                    parsed_data = []
                    for item in data:
                        parsed_data.append({
                            'start_time': item[0],
                            'end_time': item[1],
                            'entry_id': item[2],
                        })
                    return parsed_data
            except sqlite3.OperationalError:
                conn.rollback()
                return False

    @staticmethod
    def get_assosciated_cards(event_name):
        with sqlite3.connect(DB_PATH) as conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    """
                    SELECT card_identifier FROM stdn_event_cards WHERE event_name = ?
                    """,
                    (event_name,),
                )
                data = cur.fetchall()
                parsed_data = []
                for item in data:
                    parsed_data.append(item[0])
                return parsed_data
            except sqlite3.OperationalError:
                conn.rollback()
                return False

    @staticmethod
    def assosciate_card(event_name, card_id):
        with sqlite3.connect(DB_PATH) as conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO stdn_event_cards (event_name, card_identifier)
                    VALUES (?, ?)
                    """,
                    (event_name, card_id),
                )
                conn.commit()
                return True
            except sqlite3.OperationalError as err:
                logging.error(err, exc_info=err)
                conn.rollback()
                return False
            except sqlite3.IntegrityError as err:
                logging.error(err, exc_info=err)
                conn.rollback()
                raise events.EventCardAssosciationError()

    @staticmethod
    def create(name, onetime):
        with sqlite3.connect(DB_PATH) as conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO stdn_events (name, onetime)
                    VALUES (?, ?)
                    """,
                    (name, onetime),
                )
                conn.commit()
                return True
            except sqlite3.OperationalError:
                conn.rollback()
                return False
            except sqlite3.IntegrityError:
                conn.rollback()
                raise events.EventExistingError()

    @staticmethod
    def parse_time_string(time_str:str):
        assumed_format = "%d/%m/%Y %I:%M %p"
        try:
            return datetime.datetime.strptime(time_str, assumed_format)
        except ValueError:
            return False

    @staticmethod
    def schedule(name, start_time, end_time):
        if type(start_time) is str:
            start_time = events.parse_time_string(start_time)
        if type(end_time) is str:
            end_time = events.parse_time_string(end_time)

        if start_time is False or end_time is False:
            raise events.TimeError()

        with sqlite3.connect(DB_PATH) as conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO stdn_events_schedule (event_name, start_time, end_time)
                    VALUES (?, ?, ?)
                    """,
                    (name, start_time, end_time),
                )
                conn.commit()
                return True
            except sqlite3.OperationalError as err:
                logging.error("There was an error scheduling the event!", exc_info=err)
                conn.rollback()
                return False
            except sqlite3.IntegrityError:
                conn.rollback()
                raise events.EventSchedulingError()

class eventlogs:
    @staticmethod
    def set_channel(channel_id):
        data = {
            "event_channel": {
                "id": channel_id,
            }
        }
        with open('library/config.json', 'w') as f:
            json.dump(data, f, indent=4)

        return True

    @staticmethod
    def get_channel():
        with open('library/config.json', 'r') as f:
            data = json.load(f)
            return data["event_channel"]["id"]

    @staticmethod
    async def log_event(event_title, event_text):
        embed = (
            hikari.Embed(
                title="Event Log",
                description=f"Event Log of {datetime.datetime.now().strftime('%d/%m/%Y %I:%M %p')}",
                color=0x00FF00,
            )
            .add_field(
                name=event_title,
                value=event_text,
                inline=False
            )
        )

        await botapp.rest.create_message(
            eventlogs.get_channel(),
            embed=embed,
        )
        return True