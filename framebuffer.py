import requests
import time
import threading
from threading import Thread
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

def rgb565(r, g, b):
    r5 = (r * 31 + 127) // 255
    g6 = (g * 63 + 127) // 255
    b5 = (b * 31 + 127) // 255
    return struct.pack("<H", (r5 << 11) | (g6 << 5) | b5)

def build_frame():
    fd = os.open(FB, os.O_RDWR)
    buf = mmap.mmap(fd, LINE_LEN * H, mmap.MAP_SHARED, mmap.PROT_WRITE | mmap.PROT_READ)

    for y in range(H):
        row = bytearray(LINE_LEN)
        for x in range(W):
            if 100 <= y <= 200 and 100 <= x <= 200:
                r = x * 255 // (W - 1)
                g = y * 255 // (H - 1)
                b = 0
            else:
                r = x * 135 // (W - 1)
                g = x * 135 // (H - 1)
                b = 40
            row[2*x:2*x+2] = rgb565(r, g, b)
        buf.seek(y * LINE_LEN)
        buf.write(row)

    buf.flush()
    buf.close()
    os.close(fd)

Thread(target=updates, daemon=True).start()
Thread(target=build_frame, daemon=True).start()

while True:
    time.sleep(1)