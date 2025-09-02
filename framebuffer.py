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
                time.sleep(5)
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

def pack_rgb565_from_array(rgb):
    r = rgb[..., 0] & 0xF8
    g = rgb[..., 1] & 0xFC
    b = rgb[..., 2] >> 3
    return ((r << 8) | (g << 3) | b).astype(np.uint16)

def build_image(frame, text, x, y, width, height):
    text=str(text)
    img = Image.new("RGB", (width, height), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    draw.text((5, 5), text, font=font, fill=(255, 255, 255))
    rgb = np.array(img, dtype=np.uint8)
    r = (rgb[..., 0] & 0xF8).astype(np.uint16)
    g = (rgb[..., 1] & 0xFC).astype(np.uint16)
    b = (rgb[..., 2] >> 3).astype(np.uint16)
    text_block = (r << 8) | (g << 3) | b
    H, W = frame.shape
    if x >= W or y >= H or width <= 0 or height <= 0:
        return text_block
    w_fit = min(width,  W - x)
    h_fit = min(height, H - y)
    frame[y:y+h_fit, x:x+w_fit] = text_block[:h_fit, :w_fit]
    return text_block

def build_frame():
    global status
    global old_Status
    with open(FB, "r+b") as fb:
        frame = np.zeros((H, W), dtype=np.uint16)
        grey=pack_rgb565(135, 135, 135)
        red = np.uint16(0xF800)
        frame[:, :] = pack_rgb565(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        while True:
            if old_Status != status:
                status["print"]["bed_temper"]
                build_image(frame, str(status["print"]["nozzle_temper"]), 100, 100, 500, 200)
            # frame[50:150, 50:150] = grey

            fb.seek(0)
            fb.write(frame.tobytes())
            time.sleep(0.1)

Thread(target=updates, daemon=True).start()
Thread(target=build_frame, daemon=True).start()

while True:
    time.sleep(1)