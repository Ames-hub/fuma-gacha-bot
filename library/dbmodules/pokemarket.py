from library.dbmodules.dbcards import spawn_card
from library.botapp import botapp
import sqlite3
import logging
import re

DB_PATH = botapp.d['DB_PATH']

class ItemNonexistence(Exception):
    def __init__(self):
        pass

def add_item(name, price, amount, item_type):
    if item_type not in [0,1]:
        raise ValueError("Invalid item type!")

    with sqlite3.connect(DB_PATH) as conn:
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO pokeshop_stock (item_id, price, amount, item_type)
                VALUES (?, ?, ?, ?)
                """,
                (name, price, amount, item_type),
            )
            conn.commit()
            return True
        except sqlite3.OperationalError as err:
            conn.rollback()
            logging.error(err, exc_info=err)
            return False

def get_item_exists(item_id):
    with sqlite3.connect(DB_PATH) as conn:
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT item_id FROM pokeshop_stock WHERE item_id = ?
                """,
                (item_id,),
            )
            data = cur.fetchone()
            if data:
                return True
            else:
                return False
        except sqlite3.OperationalError as err:
            conn.rollback()
            logging.error(err, exc_info=err)
            raise err

def get_all_items():
    with sqlite3.connect(DB_PATH) as conn:
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT item_id, price, amount, item_type FROM pokeshop_stock
                """
            )
            data = cur.fetchall()
            parsed_data = []
            for item in data:
                parsed_data.append({
                    'item_id': item[0],
                    'price': item[1],
                    'amount': item[2],
                    'type': item[3],
                })
            return parsed_data
        except sqlite3.OperationalError as err:
            conn.rollback()
            logging.error(err, exc_info=err)
            raise err

def get_item(item_id):
    with sqlite3.connect(DB_PATH) as conn:
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT item_id, price, amount, item_type, filter_arg FROM pokeshop_stock WHERE item_id = ?
                """,
                (item_id,)
            )
            data = cur.fetchone()
            return {
                'item_id': data[0],
                'price': data[1],
                'amount': data[2],
                'type': data[3],
                'filter': data[4],
            }
        except sqlite3.OperationalError as err:
            conn.rollback()
            logging.error(err, exc_info=err)
            raise err

def filtered_pull_card(filter_string=None, **filters):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Parse filter string like "<rarity=5><card_tier=2>"
    if filter_string:
        pattern = re.findall(r"<(.*?)>", filter_string)
        for pair in pattern:
            if '=' in pair:
                key, val = pair.split('=', 1)
                key = key.strip()
                val = val.strip()
                # Convert types for known integer/boolean fields
                if key in ['rarity', 'card_tier']:
                    val = int(val)
                elif key == 'pullable':
                    val = val.lower() in ['true', '1', 'yes']
                filters[key] = val

    # Build WHERE clause
    conditions = []
    values = []

    for key, value in filters.items():
        conditions.append(f"{key} = ?")
        values.append(value)

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    query = f"""
    SELECT identifier, name, description, rarity, card_tier, pullable, "group"
    FROM global_cards
    WHERE {where_clause}
    ORDER BY RANDOM()
    LIMIT 1
    """

    cursor.execute(query, values)
    data = cursor.fetchone()
    if not data:
        raise ItemNonexistence()

    return {
        "identifier": data[0],
        "name": data[1],
        "description": data[2],
        "rarity": data[3],
        "tier": data[4],
        "pullable": data[5],
        "group": data[6],
    }

def give_pack(user_id, item_id):
    pack = get_item(item_id)

    if pack['type'] == 0:  # Randomised pack
        for i in range(pack['amount']):
            card = filtered_pull_card(
                filter_string=pack['filter'],
            )

            success = spawn_card(card['identifier'], amount=1, user_id=user_id)

            if not success:
                return False

        return True
    else:
        raise ValueError("Invalid item type!")