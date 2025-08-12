from library.dbmodules.shared import parse_time_string, TimeError
from library.botapp import botapp
import sqlite3
import logging

DB_PATH = botapp.d['DB_PATH']

class NotSchedulable(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return "Not Schedulable"

class EventExistingError(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return "Event already exists and cannot be created again."

class EventSchedulingError(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return "Event scheduling failed."

class EventCardAssosciationError(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return "Event card assosciation failed."

def delete_schedule(entry_id):
    with sqlite3.connect(DB_PATH) as conn:
        try:
            cur = conn.cursor()
            cur.execute(
                """
                DELETE FROM stdn_events_schedule WHERE entry_id = ?
                """,
                (entry_id,),
            )
            conn.commit()
            return True
        except sqlite3.OperationalError:
            conn.rollback()
            return False

def get_all_events(active_only: bool = False):
    with sqlite3.connect(DB_PATH) as conn:
        try:
            cur = conn.cursor()

            if active_only:
                query = """
                SELECT e.name
                FROM stdn_events AS e
                WHERE e.schedulable = True
                  AND EXISTS (
                      SELECT 1
                      FROM stdn_events_schedule AS s
                      WHERE s.event_name = e.name
                        AND s.start_time <= datetime('now')
                        AND s.end_time   >= datetime('now')
                  )
                """
                cur.execute(query)
            else:
                query = "SELECT name FROM stdn_events"
                cur.execute(query)

            data = cur.fetchall()
            return [row[0] for row in data]
        except sqlite3.OperationalError as err:
            logging.error(err, exc_info=err)
            conn.rollback()
            return False

def get_event_schedule(event_name):
    with sqlite3.connect(DB_PATH) as conn:
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT start_time, end_time, entry_id FROM stdn_events_schedule WHERE event_name = ?
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
                SELECT card_identifier FROM stdn_event_cards WHERE event_name = ?
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
                INSERT INTO stdn_event_cards (event_name, card_identifier)
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
            raise EventCardAssosciationError()

def create(name, onetime):
    with sqlite3.connect(DB_PATH) as conn:
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO stdn_events (name, schedulable, onetime)
                VALUES (?, ?, ?)
                """,
                (name, True, onetime),
            )
            conn.commit()
            return True
        except sqlite3.OperationalError as err:
            logging.error(err, exc_info=err)
            conn.rollback()
            return False
        except sqlite3.IntegrityError:
            conn.rollback()
            raise EventExistingError()

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
                SELECT onetime, schedulable FROM stdn_events WHERE name = ?
                """,
                (name,),
            )
            conn.commit()

            data = cur.fetchone()
            is_onetime = bool(data[0])
            is_schedulable = bool(data[1])
        except sqlite3.OperationalError as err:
            logging.error("There was an error scheduling the event!", exc_info=err)
            conn.rollback()
            return False

        if is_onetime and is_schedulable:
            cur.execute(
                """
                UPDATE stdn_events SET schedulable = False WHERE name = ?
                """,
                (name,),
            )
            conn.commit()

        if not is_schedulable:
            raise NotSchedulable()

        try:
            cur.execute(
                """
                INSERT INTO stdn_events_schedule (event_name, start_time, end_time)
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
            raise EventSchedulingError()