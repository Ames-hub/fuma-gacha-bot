from library.botapp import botapp
import datetime
import sqlite3
import logging
import hikari

DB_PATH = botapp.d['DB_PATH']

async def send_notification(target_id:int, msg_body:str, title:str="Notification Incoming!", colour:hex=None):
    target_id = int(target_id)
    msg_body = str(msg_body).strip()

    embed = (
        hikari.Embed(
            title=title,
            description=msg_body,
            timestamp=datetime.datetime.now(datetime.timezone.utc),
            colour=colour
        )
        .set_footer(
            text="You're receiving this because you enabled notifications, you can run `/notifs toggle` to disable these!"
        )
    )

    try:
        dmc = await botapp.rest.create_dm_channel(target_id)
        embed = await dmc.send(embed)
        return True
    except (hikari.ForbiddenError, hikari.UnauthorizedError):
        return False

def get_notifs_enabled(user_id:int):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        try:
            cur.execute(
                """
                SELECT enabled FROM user_notifs WHERE user_id = ?
                """,
                (user_id,)
            )
            data = cur.fetchone()
            if data:
                return bool(data[0])
            else:
                return False
        except sqlite3.OperationalError as err:
            logging.error(f"Error fetching notification enabled for user {user_id}", exc_info=err)
            return False

def set_notifs(user_id:int, state:bool):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO user_notifs (user_id, enabled)
                VALUES (?, ?)
                ON CONFLICT (user_id) DO UPDATE SET enabled = excluded.enabled
                """,
                (user_id, state)
            )
            conn.commit()
            return True
        except sqlite3.OperationalError as err:
            logging.error(f"Error setting notifications to {state} for user {user_id}", exc_info=err)
            return False