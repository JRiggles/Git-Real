import os
from random import randrange
from ssl import create_default_context
from time import sleep

import board  # type: ignore
from adafruit_is31fl3731.charlie_wing import CharlieWing  # type: ignore
from adafruit_ntp import NTP  # type: ignore
from adafruit_requests import Session  # type: ignore
from busio import I2C  # type: ignore
from digitalio import DigitalInOut  # type: ignore
from rtc import RTC  # type: ignore
from socketpool import SocketPool  # type: ignore
from wifi import radio  # type: ignore

# TODO: battery power? (+ power management)
# IDEA: lower max_brightness when on battery power

BASE_URL = 'https://github-contributions-api.deno.dev/'
RESPONSE_TYPE = '.text?no-total=true'
USERNAME = os.getenv('USERNAME') or ''
SSID = os.getenv('CIRCUITPY_WIFI_SSID') or ''
PWD = os.getenv('CIRCUITPY_WIFI_PASSWORD') or ''

# disable the neopixel to save power
np_power = DigitalInOut(board.NEOPIXEL_POWER)
np_power.switch_to_input()

# https://learn.adafruit.com/adafruit-15x7-7x15-charlieplex-led-matrix-charliewing-featherwing

i2c = I2C(board.SCL, board.SDA)
display = CharlieWing(i2c)
WIDTH = display.width
HEIGHT = display.height
max_brightness = 64


def connect() -> Session:
    """Connect to WiFi and return a `Session` object"""
    radio.connect(SSID, PWD)
    pool = SocketPool(radio)
    # get the current time from a NTP server
    ntp = NTP(pool, server="pool.ntp.org")
    # update the system RTC to the current time
    RTC().datetime = ntp.datetime
    session = Session(pool, create_default_context())
    return session


def get_data(session) -> str:
    """Get GitHub contribution data"""
    response = session.get(BASE_URL + USERNAME + RESPONSE_TYPE)
    if (status := response.status_code) == 200:
        return response.content.decode()
    else:
        return str(status)


def get_rows(data: str) -> list[map[str]]:
    """Split up the contribution data into rows of values"""
    # split response content into rows, removing the empty cell at the end
    rows = data.split('\n')
    cols = WIDTH
    # split the rows into maps of strings, keeping the last 'cols' elements and
    # removing empty element at the end
    row_maps = [map(str.strip, row.split(',')[-cols:]) for row in rows][:-1]
    return row_maps


def normalize_values(row_maps: list[map[str]]) -> list[int]:
    """
    Normalize the values in the contribution data maps to a range of
    `0` to `max_brightness` and return them as a list of `int`s
    """
    # convert string values to ints, replacing the empty strings with 0
    int_values = [
        int(n) if n.isdigit() else 0 for row in row_maps for n in row
    ]
    # normalize the integer values to a range of 0 to max_brigtness
    peak = max(int_values)
    normalized_values = [int((n / peak) * max_brightness) for n in int_values]
    return normalized_values


def update_display(led_values: list[int]) -> None:
    """Set the LEDs according to the given values"""
    for index, value in enumerate(led_values):
        y, x = divmod(index, WIDTH)
        display.pixel(x, y, value)


def randomize(frames: int) -> None:
    """Show a random array on the display for the number of `frames` given"""
    for _ in range(frames):
        for pixel in range(WIDTH * HEIGHT):
            y, x = divmod(pixel, HEIGHT)
            brightness = randrange(0, max_brightness)
            if brightness % 2:  # skew towards 0
                brightness = 0
            display.pixel(y, x, brightness)


def mainloop() -> None:
    session = connect()
    last_update_time = None
    while True:  # check for updates every hour
        if (current_hour := RTC().datetime.tm_hour) != last_update_time:
            data = get_data(session)
            rows = get_rows(data)
            led_values = normalize_values(rows)
            randomize(8)  # show refresh animation
            update_display(led_values)
            last_update_time = current_hour
        sleep(300)  # sleep for 5 minutes before checking again to save power


if __name__ == '__main__':
    mainloop()
