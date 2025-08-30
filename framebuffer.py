import requests
import time
import threading
import random
from threading import Thread
import numpy as np

# import libpyfb
def updates():
    while True:
        try:
            response = requests.get("http://127.0.0.1:5000/update")
            if response.status_code == 200:
                print("Success:", response.json())
                time.sleep(1)
            else:
                print("Error:", response.status_code, response.text)
        except requests.exceptions.ConnectionError:
            print("Server is not running!")
            time.sleep(1)
import os, mmap, struct

FB = "/dev/fb0"
W, H = 1024, 600
LINE_LEN = W * 2

def pack_rgb565(r, g, b):
    return np.uint16(((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3))

def draw_rounded_rect(frame, x, y, w, h, r, color):
    yy, xx = np.ogrid[:h, :w]
    mask = (
        (xx - r)**2 + (yy - r)**2 <= r**2 |                                # top-left corner
        (xx - (w - r - 1))**2 + (yy - r)**2 <= r**2 |                      # top-right corner
        (xx - r)**2 + (yy - (h - r - 1))**2 <= r**2 |                      # bottom-left
        (xx - (w - r - 1))**2 + (yy - (h - r - 1))**2 <= r**2              # bottom-right
    )
    sub = frame[y:y+h, x:x+w]
    sub[mask] = color

def draw_horizontal_gradient(frame, color1, color2):
    W = frame.shape[1]
    gradient = np.linspace(color1, color2, W, dtype=np.uint16)
    frame[:] = gradient

def build_frame():
    with open(FB, "r+b") as fb:
        frame = np.zeros((H, W), dtype=np.uint16)
        while True:
            red = np.uint16(0xF800)
            draw_horizontal_gradient(frame, red, grey)
            grey=pack_rgb565(135, 135, 135)
            frame[50:150, 50:150] = grey
            draw_rounded_rect(frame, 400, 500, 200, 100, 20, grey)
            fb.seek(0)
            fb.write(frame.tobytes())
            time.sleep(0.0333)

Thread(target=updates, daemon=True).start()
Thread(target=build_frame, daemon=True).start()

while True:
    time.sleep(1)