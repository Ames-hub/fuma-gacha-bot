from library.dbmodules.bugsdb import get_bug_report, create_bug_report_ticket
from library.botapp import botapp
from io import BytesIO
from PIL import Image
import datetime
import hikari
import re

class TimeError(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return "Time Error!"

async def update_user_on_bug(bug_id:int, message:str=None):
    report = get_bug_report(bugid=bug_id)
    if not report:
        raise ValueError("Bug report not found.")

    dmc = await botapp.rest.create_dm_channel(report["reporter_id"])

    embed = (
        hikari.Embed(
            title="Bug report result",
            description=f"This is regarding a bug report you filed a while ago with Ticket ID {bug_id}.\n\n",
            color=0x00ff00,
            timestamp=datetime.datetime.now().astimezone()
        )
        .add_field(
            name=f"Bug Report {bug_id}",
            value=f"Status: {"RESOLVED" if bool(report['resolved']) else "Still unresolved."}\n"
                  f"Stated Bug: {report['stated_bug']}"
        )
    )
    if message is not None:
        embed.add_field(name="Message", value=message)

    await dmc.send(embed)

def classify_severity(description: str) -> str:
    desc = description.lower()
    # Remove all symbols
    desc = re.sub(r"[^\w\s]", "", desc)

    severity_keywords = {
        "critical": ["crash", "died", "not responding", "no response", "freeze", "data loss", "cant use", "completely broken"],
        "high": ["doesnt work", "stops working", "fails", "error", "exception", "not functioning", "not working", "timeout"],
        "medium": ["slow", "lag", "delay", "inconsistent", "wrong output", "incorrect", "unexpected"],
        "low": ["typo", "formatting", "minor", "cosmetic", "alignment", "small bug"],
    }

    for severity, keywords in severity_keywords.items():
        for word in keywords:
            if word in desc:
                return severity

    # If no keywords matched, default to medium
    return "medium"

def parse_time_string(time_str:str):
    assumed_format = "%d/%m/%Y %I:%M %p"
    try:
        return datetime.datetime.strptime(time_str, assumed_format)
    except ValueError:
        return False

def combine_image(img_bytes_pack):
    pil_imgs = [Image.open(img).convert("RGBA") for img in img_bytes_pack]

    gap = 20
    total_width = sum(img.width for img in pil_imgs) + gap * (len(pil_imgs) - 1)
    max_height = max(img.height for img in pil_imgs)

    final_img = Image.new("RGBA", (total_width, max_height), (255, 255, 255, 0))

    x_offset = 0
    for img in pil_imgs:
        final_img.paste(img, (x_offset, 0))
        x_offset += img.width + gap

    img_bytes = BytesIO()
    final_img.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    image = hikari.Bytes(img_bytes.read(), "pull_result.png")
    return image

def verify_filter_string(filter_string: str):
    valid_keys = {
        'rarity': int,
        'card_tier': int,
        'pullable': bool,
        'group': str,
    }

    errors = []

    # Find all positions of < and > to locate unmatched sections
    opens = [m.start() for m in re.finditer(r"<", filter_string)]
    closes = [m.start() for m in re.finditer(r">", filter_string)]

    # Mismatched brackets?
    if len(opens) != len(closes):
        unmatched = set(opens) - set([o for o in opens if any(c > o for c in closes)])
        for pos in unmatched:
            end = len(filter_string)
            snippet = filter_string[pos:end]
            pointer = "-" * pos + "^" * len(snippet)
            errors.append(f"Mismatched angle brackets: each '<' must have a matching '>'\n{filter_string}\n{pointer}")

    # Extract all valid <...> chunks
    filters = list(re.finditer(r"<(.*?)>", filter_string))

    for match in filters:
        full = match.group(0)
        f = match.group(1)
        start = match.start()

        if '=' not in f:
            pointer = "-" * start + "^" * len(full)
            errors.append(f"Missing '=' in filter:\n{filter_string}\n{pointer}")
            continue

        key, value = f.split('=', 1)
        key = key.strip()
        value = value.strip()

        if key not in valid_keys:
            pointer = "-" * start + "^" * len(full)
            valid_keys_str = ", ".join(valid_keys.keys())
            errors.append(f"Invalid key '{key}', only {valid_keys_str} are valid keys.\n{filter_string}\n{pointer}")
            continue

        expected_type = valid_keys[key]

        try:
            if expected_type == int:
                int(value)
            elif expected_type == bool:
                if value.lower() not in ['true', 'false', '1', '0', 'yes', 'no']:
                    raise ValueError()
        except ValueError:
            pointer = "-" * start + "^" * len(full)
            errors.append(
                f"Invalid value type for '{key}' (got '{value}'):\n{filter_string}\n{pointer}"
            )

    if errors:
        return False, errors
    return True, []