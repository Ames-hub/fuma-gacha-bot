from library.botapp import botapp
import sqlite3
import secrets
import logging
import io
import re

DB_PATH = botapp.d['DB_PATH']

class NonexistantCard(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return "Nonexistant card."

def list_all(pullable_only=False):
    with sqlite3.connect(DB_PATH) as conn:
        try:
            cur = conn.cursor()
            if not pullable_only:
                cur.execute(
                    """
                    SELECT identifier, name, description, rarity, card_tier, pullable, card_group FROM global_cards
                    """
                )
            else:
                cur.execute(
                    """
                    SELECT identifier, name, description, rarity, card_tier, pullable, card_group FROM global_cards WHERE pullable = true
                    """
                )
            data = cur.fetchall()
            parsed_data = []
            for row in data:
                parsed_data.append({
                    "identifier": row[0],
                    "name": row[1],
                    "description": row[2],
                    "rarity": row[3],
                    "tier": row[4],
                    "pullable": bool(row[5]),
                    "group": row[6],
                })
            return parsed_data
        except sqlite3.OperationalError:
            conn.rollback()
            return False

def get_assosciations(card_id:str, expected_card_tier:int=None):
    card_tier = get_tier(card_id, as_number=True)

    if card_tier != expected_card_tier and expected_card_tier is not None:
        raise ValueError("Unexpected card tier.")

    if card_tier == 1:
        return []  # Normal cards have no event assosciations.
    elif card_tier == 2:
        look_location = "stdn_event_cards"
    elif card_tier == 3:
        look_location = "limited_event_cards"
    else:
        raise ValueError("Invalid card tier.")

    with sqlite3.connect(DB_PATH) as conn:
        try:
            cur = conn.cursor()
            cur.execute(
                f"""
                SELECT event_name FROM {look_location} WHERE card_identifier = ?
                """,
                (card_id,)
            )
            data = cur.fetchall()

            parsed_data = []
            for row in data:
                parsed_data.append(row[0])

            return parsed_data
        except sqlite3.OperationalError:
            conn.rollback()
            return False

def set_pullability(card_id:str, value:bool):
    with sqlite3.connect(DB_PATH) as conn:
        try:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE global_cards SET pullable = ? WHERE identifier = ?
                """,
                (value, card_id)
            )
            conn.commit()
            return True
        except sqlite3.OperationalError:
            conn.rollback()
            return False

def check_exists(card_id: str):
    with sqlite3.connect(DB_PATH) as conn:
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT EXISTS(SELECT 1 FROM global_cards WHERE identifier = ?);
                """,
                (card_id,)
            )
            return cur.fetchone()[0]
        except sqlite3.OperationalError:
            conn.rollback()
            return False

def get_tier(card_id: str, as_number=False):
    if check_exists(card_id) is False:
        raise NonexistantCard()

    with sqlite3.connect(DB_PATH) as conn:
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT card_tier FROM global_cards WHERE identifier = ?;
                """,
                (card_id,)
            )
            if as_number:
                return cur.fetchone()[0]
            else:
                return {1: "Standard", 2: "Event", 3: "Limited"}[cur.fetchone()[0]]
        except sqlite3.OperationalError:
            conn.rollback()
            return False

def spawn_card(card_id: str, amount: int, user_id: int, allow_limited:bool=False):
    if amount < 1:
        logging.info(f"Someone tried to spawn the card with the ID {card_id}, but the amount is less than 1.")
        return False

    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()

        # Step 1: Get the item details from global_cards
        # noinspection PyTypeChecker
        card_data:list = view_card(card_id)

        if len(card_data) == 0 or card_data is None:
            logging.info(f"Someone tried to spawn the card with the ID {card_id}, but it doesn't exist.")
            return False

        if len(card_data) == 1:
            card_data:dict = card_data[0]
            if card_data["tier"] == 3:
                if not allow_limited:
                    logging.info(f"Someone tried to spawn the card with the ID {card_id}, but it's limited which isn't allowed to be spawned by the user.")
                    return False

        item_identifier, item_name = card_data['identifier'], card_data['name']
        item_tier, item_rarity, item_group = card_data['tier'], card_data['rarity'], card_data['group']

        # Step 2: Check if the user already has it
        cur.execute("""
            SELECT amount FROM inventories
            WHERE user_id = ? AND item_identifier = ?
        """, (user_id, item_identifier))

        existing = cur.fetchone()
        if existing:
            cur.execute("""
                UPDATE inventories
                SET amount = amount + ?
                WHERE user_id = ? AND item_identifier = ?
            """, (amount, user_id, item_identifier))
        else:
            cur.execute("""
                INSERT INTO inventories (item_identifier, item_name, user_id, amount, item_group, item_rarity, item_tier)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (item_identifier, item_name, user_id, amount, item_group, item_rarity, item_tier))

        conn.commit()
        return True

    except sqlite3.OperationalError as err:
        logging.error("Error spawning a card.", exc_info=err)
        conn.rollback()
        return False
    finally:
        conn.close()

def add_card(card_id, name:str, description:str, rarity:int, card_tier:int, img_bytes, pullable:bool, card_group:str, era:str, is_custom:bool, card_idol:str):
    conn = sqlite3.connect(DB_PATH)

    assert card_tier in [1, 2, 3], "Card tier must be 1, 2, or 3. (1, Standard. 2, Event. 3, Limited)"
    assert type(name) is str, "Name must be a string."
    assert type(description) is str, "Description must be a string."
    assert type(rarity) is int, "Rarity must be an integer from 1 to 5."
    assert type(era) is str, "Era must be a string."
    assert type(is_custom) is bool, "Is custom must be a boolean."
    assert type(card_idol) is str, "Card idol must be a string."

    if card_id is not None:
        if type(card_id) is not str:
            return {'success': False, 'card_id': None, 'error': 'Card ID must be a string.'}
        elif " " in card_id:
            return {'success': False, 'card_id': None, 'error': 'Card ID cannot contain spaces.'}

    try:
        if card_id is None:
            card_id = secrets.token_urlsafe(6)
        cur = conn.cursor()
        cur.execute(
            f"""
            INSERT INTO global_cards (identifier, name, description, rarity, img_bytes, pullable, card_tier, card_group, card_era, is_custom, card_idol)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            {"RETURNING global_cards.identifier" if card_id is None else ""}
            """,
            (
                str(card_id),
                str(name),
                str(description),
                int(rarity),
                img_bytes,
                bool(pullable),
                int(card_tier),
                str(card_group) if card_group is not None else None,
                str(era),
                bool(is_custom),
                str(card_idol),
            ),
        )
        conn.commit()
        if card_id is None:
            return {'success': True, 'card_id': cur.fetchone()[0]}
        return {'success': True, 'card_id': card_id}
    except sqlite3.OperationalError as err:
        logging.error(err, exc_info=err)
        conn.rollback()
        return {'success': False, 'card_id': None, "error": "Critical Database Error."}
    finally:
        conn.close()

def rm_card(card_id):
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            DELETE FROM global_cards WHERE identifier = ?
            """,
            (card_id,),
        )
        conn.commit()
        return True
    except sqlite3.OperationalError as err:
        logging.error(err, exc_info=err)
        conn.rollback()
        return False
    finally:
        conn.close()

class gift_errors:
    class BadAmount(Exception):
        def __init__(self):
            self.err_code = 1
        def __str__(self):
            return "Amount must be at least 1."

    class GiverDoesNotOwnCard(Exception):
        def __init__(self):
            self.err_code = 2
        def __str__(self):
            return "Giver doesn't own the card."

    class NotEnoughOfItem(Exception):
        def __init__(self, giving, needed):
            self.err_code = 3
            self.giving = giving
            self.needed = needed
        def __str__(self):
            return f"You do not have enough quantity of that card to give. You have {self.giving}/{self.needed}."

    class GiftDBError(Exception):
        def __init__(self, err):
            self.err_code = 4
            self.err = err
        def __str__(self):
            return f"Memory error in gifting the card! {self.err}"

def gift_card(card_id: str, giving_amount: int, giver_id: int, receiver_id: int):
    if giving_amount < 1:
        raise gift_errors.BadAmount()

    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()

        # Step 1: Fetch item from the giver
        cur.execute(f"""
            SELECT item_identifier, item_name, amount FROM inventories
            WHERE user_id = ? AND item_identifier = ?
        """, (giver_id, card_id))

        item = cur.fetchone()
        if not item:
            raise gift_errors.GiverDoesNotOwnCard()

        item_identifier, item_name, giver_amount = item

        if giver_amount < giving_amount:
            raise gift_errors.NotEnoughOfItem(giver_amount, giving_amount)

        # Step 2: Deduct from giver
        if giver_amount == giving_amount:
            cur.execute("""
                DELETE FROM inventories
                WHERE user_id = ? AND item_identifier = ?
            """, (giver_id, item_identifier))
        else:
            cur.execute("""
                UPDATE inventories
                SET amount = amount - ?
                WHERE user_id = ? AND item_identifier = ?
            """, (giving_amount, giver_id, item_identifier))

        # Step 3: Add to receiver
        cur.execute("""
            SELECT amount FROM inventories
            WHERE user_id = ? AND item_identifier = ?
        """, (receiver_id, item_identifier))

        receiver_item = cur.fetchone()
        if receiver_item:
            cur.execute("""
                UPDATE inventories
                SET amount = amount + ?
                WHERE user_id = ? AND item_identifier = ?
            """, (giving_amount, receiver_id, item_identifier))
        else:
            cur.execute("""
                INSERT INTO inventories (item_identifier, item_name, user_id, amount)
                VALUES (?, ?, ?, ?)
            """, (item_identifier, item_name, receiver_id, giving_amount))

        conn.commit()
        return True

    except sqlite3.OperationalError as err:
        conn.rollback()
        return gift_errors.GiftDBError(err)
    finally:
        conn.close()

class ItemNonexistence(Exception):
    def __init__(self):
        pass

def pull_filtered_args(conn: sqlite3.Connection, filter_string, **filters) -> sqlite3.Cursor:
    cursor = conn.cursor()

    # Parse filter string like "<rarity=5><card_tier=2>"
    if filter_string:
        pattern = re.findall(r"<(.*?)>", filter_string)
        for pair in pattern:
            if '=' in pair:
                key, val = pair.split('=', 1)
                key = key.strip()
                val = val.strip()
                # Convert types for known integer/boolean fields
                if key in ['rarity', 'card_tier']:
                    val = int(val)
                elif key == 'pullable':
                    val = val.lower() in ['true', '1', 'yes']
                filters[key] = val

    # Build WHERE clause
    conditions = []
    values = []

    for key, value in filters.items():
        conditions.append(f"{key} = ?")
        values.append(value)

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    query = f"""
    SELECT identifier, name, description, rarity, card_tier, pullable, card_group
    FROM global_cards
    WHERE {where_clause}
    ORDER BY RANDOM()
    LIMIT 1
    """

    cursor.execute(query, values)
    return cursor

def filtered_get_card(filter_string=None, fetch_one:bool=True, **filters):
    conn = sqlite3.connect(DB_PATH)
    cursor = pull_filtered_args(conn, filter_string, **filters)

    if fetch_one:
        datum = cursor.fetchone()
        if not datum:
            raise ItemNonexistence()

        return {
            "identifier": datum[0],
            "name": datum[1],
            "description": datum[2],
            "rarity": datum[3],
            "tier": datum[4],
            "pullable": datum[5],
            "group": datum[6],
        }
    else:
        data = cursor.fetchall()
        if not data:
            raise ItemNonexistence()
        
        dict_list = []
        for datum in data:
            dict_list.append({
                "identifier": datum[0],
                "name": datum[1],
                "description": datum[2],
                "rarity": datum[3],
                "tier": datum[4],
                "pullable": datum[5],
                "group": datum[6],
            })
        return dict_list


def view_card(name:str):
    conn = sqlite3.connect(DB_PATH)

    # TODO: Reimplement viewing card by name. For now, we enforce "is id"
    is_id = True

    try:
        cur = conn.cursor()
        cur.execute(
            f"""
            SELECT identifier, name, description, rarity, img_bytes, card_tier, pullable, card_group, card_era, is_custom, card_idol
            FROM global_cards
            WHERE {'name' if not is_id else 'identifier'} = ?
            """,
            (name,),
        )
        data = cur.fetchall()
        conn.close()
        if data is None:
            return [{}]
        elif len(data) == 0:
            return [{}]
        elif len(data) > 1:
            parsed_data = []
            for item in data:
                parsed_data.append({
                    'identifier': str(item[0]),
                    'name': item[1],
                    'description': item[2],
                    'rarity': int(item[3]),
                    'img_bytes': item[4],
                    'tier': int(item[5]),
                    'pullable': bool(item[6]),
                    'group': item[7],
                    'era': item[8],
                    'is_custom': bool(item[9]),
                    'idol': item[10],
                })
            return parsed_data
        else:
            data = data[0]
            return [{
                'identifier': data[0],
                'name': data[1],
                'description': data[2],
                'rarity': data[3],
                'img_bytes': data[4],
                'tier': data[5],
                'pullable': bool(data[6]),
                'group': data[7],
                'era': data[8],
                'is_custom': bool(data[9]),
                'idol': data[10],
            }]
    except sqlite3.OperationalError:
        conn.rollback()
        conn.close()
        return False

def load_img_bytes(card_id):
    """
    Gets img_bytes from the database and returns it as a BytesIO object.
    """
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT img_bytes FROM global_cards WHERE identifier = ?
            """,
            (card_id,),
        )

        data = cur.fetchone()
        conn.close()
        if data is None:
            raise ValueError("Image bytes data cannot be None.")
        else:
            return io.BytesIO(data[0])
    except sqlite3.OperationalError as err:
        conn.rollback()
        conn.close()
        raise err
    except TypeError as err:
        # Sets the image to non-pullable, since something's wrong with that image.
        set_pullability(card_id, False)
        logging.warning(f"Image bytes data for card ID {card_id} is not valid, but card is still pullable. Setting to non-pullable.")
        raise err

def save_to_invent(user_id, item_identifier, item_name):
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT amount FROM inventories
            WHERE user_id = ? AND item_identifier = ?
            """,
            (user_id, item_identifier)
        )
        data = cursor.fetchone()

        if data is None:
            cursor.execute(
                """
                INSERT INTO inventories (item_identifier, item_name, user_id, amount)
                VALUES (?, ?, ?, 1)
                """,
                (item_identifier, item_name, user_id)
            )
        else:
            cursor.execute(
                """
                UPDATE inventories
                SET amount = amount + 1
                WHERE user_id = ? AND item_identifier = ?
                """,
                (user_id, item_identifier)
            )

        conn.commit()
    except sqlite3.OperationalError as e:
        conn.rollback()
        logging.error("Database error in save_to_invent: %s", e)
    finally:
        conn.close()

def pull_random_card(exception_names=None, no_limited=False):
    if exception_names is None:
        exception_names = []

    base_query = '''
    SELECT identifier, name, description, rarity, card_tier FROM global_cards WHERE pullable = True
    '''

    where_clause = ''
    if exception_names:
        placeholders = ','.join('?' for _ in exception_names)
        where_clause = f'AND identifier NOT IN ({placeholders})'
    if no_limited:
        where_clause += ' AND card_tier != 3'

    full_query = f'''
    {base_query}
    {where_clause}
    ORDER BY
        CASE rarity
            WHEN 1 THEN ABS(RANDOM()) * 1.0
            WHEN 2 THEN ABS(RANDOM()) * 1.25
            WHEN 3 THEN ABS(RANDOM()) * 1.67
            WHEN 4 THEN ABS(RANDOM()) * 5.0
            WHEN 5 THEN ABS(RANDOM()) * 8.0
            ELSE ABS(RANDOM()) * 10.0
        END
    LIMIT 1
    '''

    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()

        cursor.execute(full_query, exception_names)
        data = cursor.fetchone()
        if not data:
            return False
        else:
            return {
                "identifier": data[0],
                "name": data[1],
                "description": data[2],
                "rarity": data[3],
                "tier": data[4],
            }

    except sqlite3.OperationalError as err:
        logging.error(f"There was an error pulling a random card, {err}.\nQUERY: {full_query}", exc_info=err)
        return False
    finally:
        conn.close()