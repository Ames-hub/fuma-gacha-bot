from io import BytesIO
from PIL import Image
import datetime
import hikari

class TimeError(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return "Time Error!"

def parse_time_string(time_str:str):
    assumed_format = "%d/%m/%Y %I:%M %p"
    try:
        return datetime.datetime.strptime(time_str, assumed_format)
    except ValueError:
        return False

def combine_image(img_bytes_pack):
    if not len(img_bytes_pack) == 3:
        raise ValueError("Invalid number of images provided.")

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