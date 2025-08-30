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

def generate_smooth_noise(h, w, scale=8):
    # Base random matrix, small size
    base = np.random.rand(h//scale + 1, w//scale + 1, 3)
    # Upsample via bilinear interpolation
    y_idx = np.linspace(0, base.shape[0]-1, h)
    x_idx = np.linspace(0, base.shape[1]-1, w)
    y0 = np.floor(y_idx).astype(int)
    x0 = np.floor(x_idx).astype(int)
    y1 = np.clip(y0 + 1, 0, base.shape[0]-1)
    x1 = np.clip(x0 + 1, 0, base.shape[1]-1)

    wy = y_idx - y0
    wx = x_idx - x0

    noise = (
        (1-wy)[:, None, None]*(1-wx)[None, :, None]*base[y0[:,None], x0[None,:]] +
        wy[:, None, None]*(1-wx)[None, :, None]*base[y1[:,None], x0[None,:]] +
        (1-wy)[:, None, None]*wx[None, :, None]*base[y0[:,None], x1[None,:]] +
        wy[:, None, None]*wx[None, :, None]*base[y1[:,None], x1[None,:]]
    )
    return (noise * 255).astype(np.uint8)

def pack_rgb565_from_array(rgb):
    r = rgb[..., 0] & 0xF8
    g = rgb[..., 1] & 0xFC
    b = rgb[..., 2] >> 3
    return ((r << 8) | (g << 3) | b).astype(np.uint16)

def build_frame():
    with open(FB, "r+b") as fb:
        frame = np.zeros((H, W), dtype=np.uint16)
        grey=pack_rgb565(135, 135, 135)
        red = np.uint16(0xF800)
        while True:

            block_noise = generate_smooth_noise(600, 1024)
            frame[:, :] = pack_rgb565_from_array(block_noise)

            frame[50:150, 50:150] = grey

            fb.seek(0)
            fb.write(frame.tobytes())
            time.sleep(0.0333)

Thread(target=updates, daemon=True).start()
Thread(target=build_frame, daemon=True).start()

while True:
    time.sleep(1)