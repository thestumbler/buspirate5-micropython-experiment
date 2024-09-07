"""
splash screen (adopted from hello.py)
========

.. figure:: ../_static/hello.jpg
    :align: center

    Test for text_font_converter.

Writes "Hello!" in random colors at random locations on the Display.
https://www.youtube.com/watch?v=atBa0BYPAAc

.. note:: This example requires the following modules:

  .. hlist::
    :columns: 3

    - `st7789py`
    - `tft_config`
    - `vga2_bold_16x32`

"""

import random
import time
import st7789py as st7789
import vga2_bold_16x32 as font


def screen(disp, nloops=100, nrotations = 4, text='Hello'):
    tft = disp.tft
    for iloop in range(nloops):
        for rotation in range(nrotations):
            tft.rotation(rotation)
            tft.fill(0)
            col_max = tft.width - font.WIDTH * 5
            row_max = tft.height - font.HEIGHT
            if col_max < 0 or row_max < 0:
                raise RuntimeError(
                    "This font is too big to display on this screen."
                )
            for _ in range(50):
                tft.text(
                    font,
                    text,
                    random.randint(-10, col_max),
                    random.randint(0, row_max),
                    st7789.color565(
                        random.getrandbits(8),
                        random.getrandbits(8),
                        random.getrandbits(8),
                    ),
                    st7789.color565(
                        random.getrandbits(8),
                        random.getrandbits(8),
                        random.getrandbits(8),
                    ),
                )

def logo(disp, icon, nloops=100 ):
    tft = disp.tft
    w2 = icon.wid  << 1
    h2 = icon.hgt  << 1
    tft.fill(0)
    for iloop in range(nloops):
      # tft.fill(0)
      for _ in range(100):
        x = random.randint(0, tft.width)
        y = random.randint(0, tft.height)
        tft.blit_buffer( icon.fb, x, y, icon.wid, icon.hgt)
        time.sleep_ms(25)




