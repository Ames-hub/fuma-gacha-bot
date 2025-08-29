from library.botapp import botapp
import sqlite3
import logging

DB_PATH = botapp.d['DB_PATH']

def get_cmd_enabled(cmd_id:str):
    with sqlite3.connect(DB_PATH) as conn:
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT enabled FROM commands WHERE identifier = ?",
                (cmd_id,)
            )
            result = cur.fetchone()
            if result is None:
                logging.warning(f"Command {cmd_id} not found in database. Adding now.")
                cur.execute(
                    "INSERT INTO commands (identifier, enabled) VALUES (?, ?)",
                    (cmd_id, True)
                )
                conn.commit()
                return True
            else:
                return bool(result[0])
        except sqlite3.OperationalError as err:
            logging.error(err, exc_info=err)
            raise err