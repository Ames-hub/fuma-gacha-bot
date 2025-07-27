from library.botapp import botapp
import sqlite3
import logging

DB_PATH = botapp.d['DB_PATH']

def list_stock():
    with sqlite3.connect(DB_PATH) as conn:
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT seller_id, card_id, amount, price, time_added
                FROM nicho_market_stock
                ORDER BY time_added DESC
                """
            )
            data = cur.fetchall()
            parsed_data = []
            for item in data:
                parsed_data.append({
                    'seller_id': item[0],
                    'card_id': item[1],
                    'amount': item[2],
                    'price': item[3],
                    'time_added': item[4],
                })
            return parsed_data
        except sqlite3.OperationalError as err:
            logging.error(err, exc_info=err)
            conn.rollback()
            return False

