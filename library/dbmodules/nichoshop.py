from library.dbmodules.dbcards import view_card
from library.dbmodules.economy import account
from library.dbmodules.dbuser import userdb
from library.botapp import botapp
import sqlite3
import logging

DB_PATH = botapp.d['DB_PATH']

def get_offer(offer_id):
    with sqlite3.connect(DB_PATH) as conn:
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT offer_id, seller_id, card_id, amount, price, time_added, available, seller_disp_name
                FROM nicho_market_stock
                WHERE offer_id = ?
                """,
                (offer_id,)
            )
            data = cur.fetchone()
            if data:
                return {
                    'offer_id': data[0],
                    'seller_id': data[1],
                    'card_id': data[2],
                    'amount': data[3],
                    'price': data[4],
                    'time_added': data[5],
                    'available': data[6],
                    'seller_disp_name': data[7]
                }
            else:
                return None
        except sqlite3.OperationalError as err:
            logging.error(err, exc_info=err)
            conn.rollback()
            return False

class OfferUnavailableError(Exception):
    def __init__(self):
        pass

class OfferNotFoundError(Exception):
    def __init__(self):
        pass

def purchase_offer(offer_id, buyer_id):
    """
    A Thing which handles all the buying of stuff for nichomarket.

    Raises: OfferUnavailableError, OfferNotFoundError

    Returns: dict
    """
    offer = get_offer(offer_id)
    if offer:
        if offer['available'] == False:
            raise OfferUnavailableError()
    else:
        raise OfferNotFoundError()

    seller_id = offer['seller_id']
    seller_bank = account(seller_id)
    buyer_bank = account(buyer_id)

    # Limited packs charge Nicho Coins instead of Fuma Coins.
    offered_card = view_card(offer['card_id'])
    is_limited_pack = offered_card['tier'] == 3

    # Verifies the buyer has enough money.
    if not is_limited_pack:
        cur_bal = buyer_bank.fumacoins.balance()
    else:
        cur_bal = buyer_bank.nichocoins.balance()

    if cur_bal < offered_card['price']:
        raise buyer_bank.InsufficientFundsError(offered_card['price'], cur_bal)

    with sqlite3.connect(DB_PATH) as conn:
        try:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE nicho_market_stock SET available = False WHERE offer_id = ?
                """,
                (offer_id,)
            )
        except sqlite3.OperationalError as err:
            logging.error(err, exc_info=err)
            conn.rollback()
            return False

    # Give the money to the seller
    if not is_limited_pack:
        seller_money_given = seller_bank.fumacoins.modify_balance(offer['price'], operator="add")
        buyer_money_taken = buyer_bank.fumacoins.modify_balance(offer['price'], operator="subtract")
    else:
        seller_money_given = seller_bank.nichocoins.modify_balance(offer['price'], operator="add")
        buyer_money_taken = buyer_bank.nichocoins.modify_balance(offer['price'], operator="subtract")

    if seller_money_given and buyer_money_taken:
        money_success = True
    else:
        # Attempt to undo it since one or the other failed.
        if not is_limited_pack:
            if seller_money_given is True and not buyer_money_taken:
                seller_bank.fumacoins.modify_balance(offer['price'], operator="subtract")
            elif buyer_money_taken is True and not seller_money_given:
                buyer_bank.fumacoins.modify_balance(offer['price'], operator="add")
        else:
            if seller_money_given is True and not buyer_money_taken:
                seller_bank.nichocoins.modify_balance(offer['price'], operator="subtract")
            elif buyer_money_taken is True and not seller_money_given:
                buyer_bank.nichocoins.modify_balance(offer['price'], operator="add")
        return False

    # Give the item
    buyer = userdb(buyer_id)

    give_success = buyer.add_to_inventory(
        card_id=offer['card_id'],
        amount=offer['amount'],
        allow_limited=True
    )
    if give_success:
        return {
            'success': True,
            'money_modify': {
                'overall': money_success,
                'seller': seller_money_given,
                'buyer': buyer_money_taken,
            },
            'item_given': give_success,
            'transaction': {
                'given_card_id': offer['card_id'],
                'given_amount': offer['amount'],
                'offer_id': offer_id
            }
        }
    else:
        with sqlite3.connect(DB_PATH) as conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    """
                    UPDATE nicho_market_stock SET available = True WHERE offer_id = ?
                    """,
                    (offer_id,)
                )
            except sqlite3.OperationalError as err:
                logging.error(err, exc_info=err)
                conn.rollback()

        return {
            'success': False,
            'money_modify': {
                'overall': money_success,
                'seller': seller_money_given,
            },
            'transaction': {
                'given_card_id': offer['card_id'],
                'given_amount': offer['amount'],
                'offer_id': offer_id
            }
        }

def delete_offer(offer_id):
    with sqlite3.connect(DB_PATH) as conn:
        try:
            cur = conn.cursor()
            cur.execute(
                """
                DELETE FROM nicho_market_stock WHERE offer_id = ?
                """,
                (offer_id,),
            )
            conn.commit()
            return True
        except sqlite3.OperationalError:
            conn.rollback()
            return False

def add_offer(seller_id, seller_disp_name, card_id, amount, price):
    """
    Handles the full process of adding an offer to the nichomarket.
    """
    # Removes the item from the inventory.
    user = userdb(seller_id)

    rm_success = user.remove_from_inventory(card_id=card_id, amount=amount)
    offer_id = add_selling_item(seller_id, seller_disp_name, card_id, amount, price)

    sell_success = type(offer_id) is int

    if rm_success and sell_success:
        return offer_id
    else:
        # Undo both successful actions.
        if rm_success:
            user.add_to_inventory(card_id=card_id, amount=amount)
        if offer_id:
            delete_offer(offer_id)

        return False

def add_selling_item(seller_id, seller_disp_name, card_id, amount, price):
    """
    One step of the full process of adding an offer to the nichomarket. This one just adds the item and amount to the DB
    As a possible offer.
    """
    seller_id = int(seller_id)
    card_id = str(card_id)
    amount = int(amount)
    price = int(price)
    with sqlite3.connect(DB_PATH) as conn:
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO nicho_market_stock (seller_id, seller_disp_name, card_id, amount, price)
                VALUES (?, ?, ?, ?, ?)
                """,
                (seller_id, seller_disp_name, card_id, amount, price),
            )
            conn.commit()
            # Get offer ID assosciated.
            offer_id = cur.lastrowid
            return offer_id
        except sqlite3.OperationalError as err:
            logging.error(err, exc_info=err)
            conn.rollback()
            return False
        except sqlite3.IntegrityError:
            conn.rollback()
            raise

def list_stock():
    with sqlite3.connect(DB_PATH) as conn:
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT offer_id, seller_id, card_id, amount, price, time_added, available, seller_disp_name
                FROM nicho_market_stock
                ORDER BY time_added DESC
                """
            )
            data = cur.fetchall()
            parsed_data = []
            for item in data:
                parsed_data.append({
                    'offer_id': item[0],
                    'seller_id': item[1],
                    'card_id': item[2],
                    'amount': item[3],
                    'price': item[4],
                    'time_added': item[5],
                    'available': item[6],
                    'seller_disp_name': item[7],
                })
            return parsed_data
        except sqlite3.OperationalError as err:
            logging.error(err, exc_info=err)
            conn.rollback()
            return False

