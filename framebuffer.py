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

def build_frame():
    with open(FB, "r+b") as fb:
        while True:
            red = np.uint16(0xF800)
            frame = np.full((H, W), pack_rgb565(random.randint(0, 255),random.randint(0, 255),random.randint(0, 255)), dtype=np.uint16)
            grey=pack_rgb565(135, 135, 135)
            frame[50:150, 50:150] = grey
            fb.seek(0)
            fb.write(frame.tobytes())

Thread(target=updates, daemon=True).start()
Thread(target=build_frame, daemon=True).start()

while True:
    time.sleep(1)