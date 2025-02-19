#!/usr/bin/env python3
import math
import sys
import time

from PIL import Image, ImageDraw

import st7789

# Higher SPI bus speed = higher framerate
try:
    SPI_SPEED_MHZ = int(sys.argv[1])
except ValueError:
    sys.exit(1)
except IndexError:
    SPI_SPEED_MHZ = 80

try:
    display_type = sys.argv[2]
except IndexError:
    display_type = "square"

print(
    f"""
framerate.py - Test LCD framerate.

If you're using Breakout Garden, plug the 1.3" LCD (SPI)
breakout into the front slot.

Usage: {sys.argv[0]} <spi_speed_mhz> <display_type>

Where <display_type> is one of:
  * square - 240x240 1.3" Square LCD
  * round  - 240x240 1.3" Round LCD (applies an offset)
  * rect   - 240x135 1.14" Rectangular LCD (applies an offset)
  * dhmini - 320x240 2.0" Rectangular LCD

Running at: {SPI_SPEED_MHZ}MHz on a {display_type} display.
"""
)

try:
    width, height, rotation, backlight, offset_left, offset_top = {
        "square": (240, 240, 90, 19, 0, 0),
        "round": (240, 240, 90, 19, 40, 0),
        "rect": (240, 135, 0, 19, 40, 53),
        "dhmini": (320, 240, 180, 13, 0, 0),
    }[display_type]
except IndexError:
    raise RuntimeError(f"Unsupported display type: {display_type}")

# Create ST7789 LCD display class.
disp = st7789.ST7789(
    width=width,
    height=height,
    rotation=rotation,
    port=0,
    cs=st7789.BG_SPI_CS_FRONT,  # BG_SPI_CS_BACK or BG_SPI_CS_FRONT
    dc=9,
    backlight=19,  # Breakout Garden: 18 for back slot, 19 for front slot.
                   # NOTE: Change this to 13 for Pirate Audio boards
    spi_speed_hz=SPI_SPEED_MHZ * 1000000,
    offset_left=offset_left,
    offset_top=offset_top,
)

WIDTH = disp.width
HEIGHT = disp.height
STEPS = WIDTH * 2
images = []

for step in range(STEPS):
    image = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 128))
    draw = ImageDraw.Draw(image)

    if step % 2 == 0:
        draw.rectangle((WIDTH / 2, int(HEIGHT / 2), WIDTH, HEIGHT), (0, 128, 0))
    else:
        draw.rectangle((0, 0, WIDTH / 2 - 1, int(HEIGHT / 2) - 1), (0, 128, 0))

    f = math.sin((float(step) / STEPS) * math.pi)
    offset_left = int(f * WIDTH)
    draw.ellipse((offset_left, 35, offset_left + 10, 45), (255, 0, 0))

    images.append(image)

count = 0
time_start = time.time()

while True:
    disp.display(images[count % len(images)])
    count += 1
    time_current = time.time() - time_start
    if count % 120 == 0:
        print(
            f"Time: {time_current:8.3f},      Frames: {count:6d},      FPS: {count / time_current:8.3f}"
        )
