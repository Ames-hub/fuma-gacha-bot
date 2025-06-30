from library.botapp import botapp
import sqlite3
import logging
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
                "identifier": "TEXT NOT NULL PRIMARY KEY DEFAULT (lower(hex(randomblob(3))))",
                'name': 'TEXT NOT NULL',
                'description': 'TEXT NOT NULL',
                'rarity': 'INTEGER NOT NULL DEFAULT 1',
                'img_bytes': 'BLOB',
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

def has_admin_role(role_ids):
    admin_roles = botapp.d['admin_roles']
    for role_id in role_ids:
        for admin_role_id in admin_roles:
            if role_id == admin_role_id:
                return True
    return False

def view_card(name:str):
    conn = sqlite3.connect(DB_PATH)

    is_id = " " not in name and name.lower().startswith("id:")
    if is_id:
        name = name.replace("id:", "")

    try:
        cur = conn.cursor()
        cur.execute(
            f"""
            SELECT identifier, name, description, rarity, img_bytes
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
            }]
    except sqlite3.OperationalError:
        conn.rollback()
        conn.close()
        return False

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

def pull_random_card(exception_names=None):
    if exception_names is None:
        exception_names = []

    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()

        base_query = '''
        SELECT identifier, name, description, rarity FROM global_cards
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
