from library.dbmodules.shared import parse_time_string, TimeError
from library.botapp import botapp
import sqlite3
import logging

DB_PATH = botapp.d['DB_PATH']

class LimEventExistingError(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return "Event already exists and cannot be created again."

class LimEventSchedulingError(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return "Event scheduling failed."

class LimEventCardAssosciationError(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return "Event card assosciation failed."

class NotSchedulable(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return "Not Schedulable"

def delete_schedule(entry_id):
    with sqlite3.connect(DB_PATH) as conn:
        try:
            cur = conn.cursor()
            cur.execute(
                """
                DELETE FROM limited_events_schedule WHERE entry_id = ?
                """,
                (entry_id,),
            )
            conn.commit()
            return True
        except sqlite3.OperationalError:
            conn.rollback()
            return False

def get_all_events():
    with sqlite3.connect(DB_PATH) as conn:
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT name FROM limited_events
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

def get_event_schedule(event_name):
    with sqlite3.connect(DB_PATH) as conn:
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT start_time, end_time, entry_id FROM limited_events_schedule WHERE event_name = ?
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

def get_assosciated_cards(event_name):
    with sqlite3.connect(DB_PATH) as conn:
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT card_identifier FROM limited_event_cards WHERE event_name = ?
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

def assosciate_card(event_name, card_id):
    with sqlite3.connect(DB_PATH) as conn:
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO limited_event_cards (event_name, card_identifier)
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
            raise LimEventCardAssosciationError()

def create(name):
    with sqlite3.connect(DB_PATH) as conn:
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO limited_events (name, schedulable)
                VALUES (?, True)
                """,
                (name,),
            )
            conn.commit()
            return True
        except sqlite3.OperationalError:
            conn.rollback()
            return False
        except sqlite3.IntegrityError:
            conn.rollback()
            raise LimEventExistingError()

def schedule(name, start_time, end_time):
    if type(start_time) is str:
        start_time = parse_time_string(start_time)
    if type(end_time) is str:
        end_time = parse_time_string(end_time)

    if start_time is False or end_time is False:
        raise TimeError()

    with sqlite3.connect(DB_PATH) as conn:
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT schedulable FROM limited_events WHERE name = ?
                """,
                (name,),
            )
            conn.commit()

            data = cur.fetchone()
            is_schedulable = bool(data[0])
        except sqlite3.OperationalError as err:
            logging.error("There was an error scheduling the event!", exc_info=err)
            conn.rollback()
            return False

        if is_schedulable:
            cur.execute(
                """
                UPDATE limited_events SET schedulable = False WHERE name = ?
                """,
                (name,),
            )
            conn.commit()

        if not is_schedulable:
            raise NotSchedulable()

        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO limited_events_schedule (event_name, start_time, end_time)
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
            raise LimEventSchedulingError()