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

def is_administrator(users_roles:list, user_id):
    admin_roles = botapp.d['admin_roles']
    admin_ids = botapp.d['admin_ids']

    for admin_user_id in admin_ids:
        if admin_user_id == user_id:
            return True

    for admin_role in admin_roles:
        for user_role in users_roles:
            if int(admin_role) == int(user_role):
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

def get_inventory(user_id, card_id=None, card_name=None, card_group=None, card_rarity=None, card_tier=None):
    conn = sqlite3.connect(DB_PATH)
    user_id = int(user_id)

    args = (user_id,)
    if card_id is not None:
        args += (card_id,)
    if card_name is not None:
        args += (card_name,)
    if card_group is not None:
        args += (card_group,)
    if card_rarity is not None:
        args += (card_rarity,)
    if card_tier is not None:
        args += (card_tier,)

    try:
        cursor = conn.cursor()
        cursor.execute(
            f"""
            SELECT item_name, item_identifier, amount, item_group, item_rarity, item_tier
            FROM inventories
            WHERE user_id = ?
            {"AND item_identifier = ?" if card_id is not None else ""}
            {"AND item_name = ?" if card_name is not None else ""}
            {"AND item_group = ?" if card_group is not None else ""}
            {"AND item_rarity = ?" if card_rarity is not None else ""}
            {"AND item_tier = ?" if card_tier is not None else ""}
            ORDER BY amount DESC
            """,
            args,
        )
        data = cursor.fetchall()

        inventory = {}
        for row in data:
            inventory[row[1]] = {
                "name": row[0],
                "identifier": row[1],
                "amount": row[2],
                "group": row[3],
                "rarity": row[4],
                "tier": row[5],
            }

        return inventory
    except sqlite3.OperationalError as err:
        conn.rollback()
        logging.error(f"An error occurred while running a command: {err}", exc_info=err)
    finally:
        conn.close()
class invent_errs:
    class TooFewItemsError(Exception):
        """For when an item exists, but you try to use more than you have of it."""
        def __init__(self, amount_needed, user_has):
            self.amount_needed = amount_needed
            self.user_has = user_has

        def __str__(self):
            return f"You need {self.amount_needed - self.user_has} more item(s) of that type to do that"

    class InventoryItemNotFound(Exception):
        """For when an item does not exist in the inventory."""
        def __init__(self):
            pass

# A class meant to make things slightly more convenient.
class userdb:
    def __init__(self, user_id:int):
        self.user_id = int(user_id)
        self.bank:account = account(user_id)

    def add_to_inventory(self, card_id, amount=1, allow_limited=False):
        from library.dbmodules.dbcards import spawn_card
        return spawn_card(
            card_id=card_id,
            user_id=self.user_id,
            amount=amount,
            allow_limited=allow_limited
        )

    def remove_from_inventory(self, card_id, amount):
        """
        Remove a specified amount of an item from the user's inventory.

        Returns:
            bool: True if the removal succeeded.
        """
        # Validate inputs
        if card_id is None or str(card_id).strip() == "":
            raise ValueError("card_id must be a non-empty value.")
        try:
            amt = int(amount)
        except (TypeError, ValueError):
            raise ValueError("amount must be an integer.")
        if amt <= 0:
            raise ValueError("amount must be greater than 0.")

        item_identifier = str(card_id)

        with sqlite3.connect(DB_PATH) as conn:
            try:
                # Manage transaction explicitly for safety against concurrent writers
                cur = conn.cursor()

                # Read the current amount
                cur.execute(
                    """
                    SELECT amount
                    FROM inventories
                    WHERE user_id = ? AND item_identifier = ?
                    """,
                    (self.user_id, item_identifier),
                )
                row = cur.fetchone()
                if row is None:
                    conn.rollback()
                    raise invent_errs.InventoryItemNotFound()

                current_amount = int(row[0])
                if current_amount < amt:
                    conn.rollback()
                    raise invent_errs.TooFewItemsError(amt, current_amount)

                # Update ensures we never go below zero even with concurrency
                cur.execute(
                    """
                    UPDATE inventories
                    SET amount = amount - ?
                    WHERE user_id = ? AND item_identifier = ? AND amount >= ?
                    """,
                    (amt, self.user_id, item_identifier, amt),
                )
                if cur.rowcount != 1:
                    conn.rollback()
                    return False

                conn.commit()
                return True
            except sqlite3.OperationalError as err:
                logging.error("Database operation failed while removing from inventory", exc_info=err)
                return False

    def get_inventory(self):
        return get_inventory(self.user_id)