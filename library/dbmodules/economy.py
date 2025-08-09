from library.botapp import botapp
import sqlite3
import logging

DB_PATH = botapp.d['DB_PATH']

class _fumacoins:
    def __init__(self, user_id:int,):
        self.user_id = int(user_id)

    def balance(self):
        with sqlite3.connect(DB_PATH) as conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    """
                    SELECT fumacoins FROM economy_bank WHERE user_id = ?
                    """,
                    (self.user_id,)
                )
                data = cur.fetchone()
                if data:
                    return data[0]
                else:
                    return 0
            except sqlite3.OperationalError as err:
                logging.error(err, exc_info=err)
                conn.rollback()
                return 0

    def modify_balance(self, amount, operator:str):
        if operator in ['+', 'add']:
            operator = "+"
        elif operator in ['-', 'sub', 'subtract']:
            operator = "-"
        else:
            raise ValueError("Invalid operator provided.")

        cur_bal = self.balance()
        if operator == "-":
            # Do not let it put your balance into the negative.
            if cur_bal < amount:
                amount = cur_bal

        with sqlite3.connect(DB_PATH) as conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    f"""
                        INSERT INTO economy_bank (user_id, fumacoins)
                        VALUES (?, ?)
                        ON CONFLICT(user_id) DO UPDATE SET fumacoins = fumacoins {operator} EXCLUDED.fumacoins
                    """,
                    (self.user_id, amount)
                )
                conn.commit()
                return True
            except sqlite3.OperationalError as err:
                logging.error(err, exc_info=err)
                conn.rollback()
                return False
            except sqlite3.IntegrityError:
                conn.rollback()

class _nichocoins:
    def __init__(self, user_id:int,):
        self.user_id = int(user_id)

    def balance(self):
        with sqlite3.connect(DB_PATH) as conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    """
                    SELECT nichocoins FROM economy_bank WHERE user_id = ?
                    """,
                    (self.user_id,)
                )
                data = cur.fetchone()
                if data:
                    return data[0]
                else:
                    return 0
            except sqlite3.OperationalError as err:
                logging.error(err, exc_info=err)
                conn.rollback()
                return 0

    def modify_balance(self, amount, operator:str):
        if operator in ['+', 'add']:
            operator = "+"
        elif operator in ['-', 'sub', 'subtract']:
            operator = "-"
        else:
            raise ValueError("Invalid operator provided.")

        with sqlite3.connect(DB_PATH) as conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    f"""
                        INSERT INTO economy_bank (user_id, nichocoins)
                        VALUES (?, ?)
                        ON CONFLICT(user_id) DO UPDATE SET nichocoins = nichocoins {operator} EXCLUDED.nichocoins
                    """,
                    (self.user_id, amount)
                )
                conn.commit()
                return True
            except sqlite3.OperationalError as err:
                logging.error(err, exc_info=err)
                conn.rollback()
                return False
            except sqlite3.IntegrityError:
                conn.rollback()

class account:
    def __init__(self, user_id):
        self.user_id = int(user_id)

        self.fumacoins:_fumacoins = _fumacoins(user_id)
        self.nichocoins:_nichocoins = _nichocoins(user_id)

    class InsufficientFundsError(Exception):
        def __init__(self, amount_needed, user_has):
            self.amount_needed = amount_needed
            self.user_has = user_has