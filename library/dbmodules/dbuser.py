from library.dbmodules.economy import account
from library.botapp import botapp
import sqlite3
import logging

DB_PATH = botapp.d['DB_PATH']

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

def is_administrator(user_id):
    admin_ids = botapp.d['admin_ids']
    for admin_id in admin_ids:
        if int(user_id) == int(admin_id):
            return True
    return False

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

# A class meant to make things slightly more convenient.
class userdb:
    def __init__(self, user_id:int):
        self.user_id = int(user_id)
        self.bank:account = account(user_id)

    def add_to_inventory(self, card_id, amount=1):
        from library.dbmodules.dbcards import spawn_card
        return spawn_card(
            card_id=card_id,
            user_id=self.user_id,
            amount=amount,
        )

    def get_inventory(self):
        return get_inventory(self.user_id)