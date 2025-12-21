from cogs.donutshop.buy_view.buy_choice_pack_view import main_view
from library.botapp import botapp, miru_client
from library.dbmodules import dbcards
import lightbulb
import sqlite3
import logging
import hikari

DB_PATH = botapp.d['DB_PATH']

def add_item(name, price, amount, item_type, filter_arg):
    if item_type not in [0,1]:
        raise ValueError("Invalid item type!")

    with sqlite3.connect(DB_PATH) as conn:
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO pokeshop_stock (item_id, price, amount, item_type, filter_arg)
                VALUES (?, ?, ?, ?, ?)
                """,
                (str(name), int(price), int(amount), int(item_type), str(filter_arg)),
            )
            conn.commit()
            return True
        except sqlite3.OperationalError as err:
            conn.rollback()
            logging.error(err, exc_info=err)
            return False

def delete_item(item_id):
    with sqlite3.connect(DB_PATH) as conn:
        try:
            cur = conn.cursor()
            cur.execute(
                """
                DELETE FROM pokeshop_stock WHERE item_id = ?
                """,
                (item_id,),
            )
            conn.commit()
            return True
        except sqlite3.OperationalError as err:
            conn.rollback()
            logging.error(err, exc_info=err)
            raise err

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
                SELECT item_id, price, amount, item_type, filter_arg FROM pokeshop_stock
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
                    'filter': item[4],
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

def give_random_pack(user_id, item_id):
    pack = get_item(item_id)

    if pack['type'] != botapp.d['packtypes']['random']:  # Randomised pack
        raise TypeError("This is not a randomised pack!")

    for i in range(pack['amount']):
        try:
            card = dbcards.filtered_get_card(
                filter_string=pack['filter'],
            )
        except dbcards.ItemNonexistence:
            return -1  # No cards fitting the criteria match.

        success = dbcards.spawn_card(card['identifier'], amount=1, user_id=user_id, allow_limited=True)

        if not success:
            return False

    return True

class choicepack_errors:
    class NotChoicePack(Exception):
        def __init__(self, pack_id):
            self.msg = f"Pack {pack_id} is not a choice pack"
            self.pack_id = pack_id
        def __str__(self):
            return self.msg

async def give_choice_pack(item_id, user_id=None, context:lightbulb.SlashContext=None):
    """
    Gives a user a 'choice' card pack, asks them what cards they want from the available options and then gives those cards.
    
    :param user_id: Description
    :param item_id: Description
    """
    user_id = int(user_id)
    item_id = int(item_id)
    if user_id is None and context is None:
        raise TypeError("user ID and context cannot both be None.")
    
    # If context is not none, send the message in the channel they bought from as ephemeral
    card_pack = get_item(item_id)
    if int(card_pack['type']) != botapp.d['packtypes']['choice']:
        # This should've never been handed to this function
        raise choicepack_errors.NotChoicePack(card_pack['item_id'])

    view = main_view()
    embed = view.gen_embed()
    viewmenu = view.init_view()
    await context.respond(
        embed=embed,
        components=viewmenu.build(),
        flags=hikari.MessageFlag.EPHEMERAL
    )
    miru_client.start_view(viewmenu)
    await viewmenu.wait()

    return True