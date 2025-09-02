import requests
import time
import threading
import random
from threading import Thread
import numpy as np
from PIL import Image, ImageDraw, ImageFont

status={}
old_Status={}

# import libpyfb
def updates():
    global status
    global old_Status
    while True:
        try:
            response = requests.get("http://127.0.0.1:5000/update")
            if response.status_code == 200:
                old_Status = status
                status = response.json()
                print(status,"\n")
                time.sleep(0.3)
            else:
                print("Error:", response.status_code, response.text)
        except requests.exceptions.ConnectionError:
            print("Server is not running!")
            time.sleep(60)

FB = "/dev/fb0"
W, H = 1024, 600
LINE_LEN = W * 2

def pack_rgb565(r, g, b):
    return np.uint16(((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3))

def build_image(frame, text, x, y, width, height, font_size=24, radius=15):
    text = str(text)
    img = Image.new("RGB", (width, height), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()
    draw.rounded_rectangle(
        [(0, 0), (width, height)],
        radius=radius,
        fill=(0, 0, 0),          # Background color
        outline=(255, 255, 255), # Border color (optional)
        width=2                  # Border thickness (optional)
    )
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_x = (width - text_width) // 2
    text_y = (height - text_height) // 2
    draw.text((text_x, text_y), text, font=font, fill=(255, 255, 255))
    rgb = np.array(img, dtype=np.uint8)
    r = (rgb[..., 0] & 0xF8).astype(np.uint16)
    g = (rgb[..., 1] & 0xFC).astype(np.uint16)
    b = (rgb[..., 2] >> 3).astype(np.uint16)
    text_block = (r << 8) | (g << 3) | b
    H, W = frame.shape
    if x >= W or y >= H or width <= 0 or height <= 0:
        return text_block
    w_fit = min(width, W - x)
    h_fit = min(height, H - y)
    frame[y:y+h_fit, x:x+w_fit] = text_block[:h_fit, :w_fit]
    return text_block


def build_image(frame, text, x, y, width, height, font_size=24, radius=15,
                bg_color=(122, 122, 122), text_color=(255, 255, 255),
                outline=(255, 255, 255)):
    text = str(text)
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()
    draw.rounded_rectangle(
        [(0, 0), (width-1, height-1)],
        radius=radius,
        fill=bg_color + (255,),                 # solid fill
        outline=(outline + (255,)) if outline else None,
        width=2
    )
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = (width - tw) // 2
    ty = (height - th) // 2
    draw.text((tx, ty), text, font=font, fill=text_color + (255,))
    H, W = frame.shape
    if x >= W or y >= H or width <= 0 or height <= 0:
        return None
    w_fit = min(width,  W - x)
    h_fit = min(height, H - y)
    src = np.array(img, dtype=np.uint8)[:h_fit, :w_fit, :]       # (h,w,4)
    src_rgb = src[..., :3].astype(np.uint16)
    alpha = (src[..., 3].astype(np.float32) / 255.0)             # (h,w)
    if np.all(alpha == 0):
        return None
    dst565 = frame[y:y+h_fit, x:x+w_fit].astype(np.uint16)
    dst_r = ((dst565 >> 11) & 0x1F).astype(np.uint16) << 3
    dst_g = ((dst565 >> 5)  & 0x3F).astype(np.uint16) << 2
    dst_b = ( dst565        & 0x1F).astype(np.uint16) << 3
    dst_rgb = np.stack([dst_r, dst_g, dst_b], axis=-1).astype(np.uint16)
    a = alpha[..., None]  # (h,w,1)
    out_rgb = (a * src_rgb.astype(np.float32) + (1.0 - a) * dst_rgb.astype(np.float32)).round()
    out_rgb = np.clip(out_rgb, 0, 255).astype(np.uint16)
    r5 = (out_rgb[..., 0] >> 3) & 0x1F
    g6 = (out_rgb[..., 1] >> 2) & 0x3F
    b5 = (out_rgb[..., 2] >> 3) & 0x1F
    out565 = (r5 << 11) | (g6 << 5) | b5
    frame[y:y+h_fit, x:x+w_fit] = out565
    return out565

def build_text(frame, text, size, x, y):
    font = ImageFont.truetype("DejaVuSans.ttf", size)
    dummy_img = Image.new("RGB", (1, 1))
    draw = ImageDraw.Draw(dummy_img)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    img = Image.new("RGB", (text_width, text_height), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.text((0, 0), text, fill=(255, 255, 255), font=font)
    rgb = np.array(img, dtype=np.uint8)
    r = (rgb[..., 0] & 0xF8).astype(np.uint16)
    g = (rgb[..., 1] & 0xFC).astype(np.uint16)
    b = (rgb[..., 2] >> 3).astype(np.uint16)
    text_block = (r << 8) | (g << 3) | b
    H, W = frame.shape
    if x >= W or y >= H:
        return
    w_fit = min(text_width, W - x)
    h_fit = min(text_height, H - y)
    frame[y:y+h_fit, x:x+w_fit] = text_block[:h_fit, :w_fit]

def build_frame():
    global status
    global old_Status
    with open(FB, "r+b") as fb:
        frame = np.zeros((H, W), dtype=np.uint16)
        grey=pack_rgb565(135, 135, 135)
        red = np.uint16(0xF800)
        frame[:, :] = grey
        while True:
            if old_Status != status:
                if str(status["print"]["gcode_state"]) == "RUNNING":
                    pass
                else:
                    pass
                if status.get("print", {}).get("nozzle_temper") is not None:
                    build_text(frame, "Nozzle Temp:", 24, 50, 50)
                    build_image(frame, str(status["print"]["nozzle_temper"]), 50, 70, 300, 80)
                else:
                    build_text(frame, "Nozzle Temp:", 24, 50, 50)
                    build_image(frame, "Waiting...", 50, 70, 300, 80)
                if status.get("print", {}).get("mc_remaining_time") is not None:
                    build_image(frame, f"{str(status['print']['mc_remaining_time'])}m", 50, 183, 300, 100)
                else:
                    build_image(frame, "Waiting...", 50, 183, 300, 100)
                if status.get("print", {}).get("layer_num") is not None:
                    build_image(frame, str(status["print"]["layer_num"]), 50, 316, 300, 100)
                else:
                    build_image(frame, "Waiting...", 50, 316, 300, 100)
                if status.get("print", {}).get("mc_percent") is not None:
                    build_image(frame, f"{str(status['print']['mc_percent'])}%", 50, 450, 300, 100)
                else:
                    build_image(frame, "Waiting...", 50, 450, 300, 100)
            # frame[50:150, 50:150] = grey

            fb.seek(0)
            fb.write(frame.tobytes())
            time.sleep(0.1)

Thread(target=updates, daemon=True).start()
Thread(target=build_frame, daemon=True).start()

while True:
    time.sleep(1)