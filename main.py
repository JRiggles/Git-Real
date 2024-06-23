import adafruit_ntp
import board
import busio
import os
import rtc
import socketpool
import ssl
import time
import wifi
from adafruit_is31fl3731.charlie_wing import CharlieWing
from adafruit_requests import Session
from random import randrange

# TODO: battery power? (+ power management)
# IDEA: lower max_brightness when on battery power

BASE_URL = 'https://github-contributions-api.deno.dev/'
RESPONSE_TYPE = '.text?no-total=true'
USERNAME = os.getenv('USERNAME')
SSID = os.getenv('CIRCUITPY_WIFI_SSID')
PWD = os.getenv('CIRCUITPY_WIFI_PASSWORD')

# https://learn.adafruit.com/adafruit-15x7-7x15-charlieplex-led-matrix-charliewing-featherwing

i2c = busio.I2C(board.SCL, board.SDA)
display = CharlieWing(i2c)
max_brightness = 255


def connect() -> Session:
    """Connect to WiFi and return a `Session` object"""
    wifi.radio.connect(SSID, PWD)
    pool = socketpool.SocketPool(wifi.radio)
    # get the current time from a NTP server
    ntp = adafruit_ntp.NTP(pool, server="pool.ntp.org", tz_offset=-4)
    current_time = ntp.datetime
    # update the system RTC
    rtc.RTC().datetime = current_time
    session = Session(pool, ssl.create_default_context())
    return session


def get_data(session) -> str:
    """Get GitHub contribution data"""
    response = session.get(BASE_URL + USERNAME + RESPONSE_TYPE)
    if (status := response.status_code) == 200:
        return response.content
    else:
        return str(status)


def get_rows(data: str) -> list[map]:
    """Split up the contribution data into rows of values"""
    # split response content into rows, removing the empty cell at the end
    rows = data.decode().split('\n')
    # split the rows into maps of strings, keeping the last 'display.width'
    # elements
    string_maps = [
        map(str.strip, row.split(',')[-display.width - 1:-1]) for row in rows
    ]
    return string_maps


def normalize_data(string_maps: list[map]) -> list[int]:
    """
    Normalize the values in the contribution data string to a range of
    `0` to `max_brightness` and return them as a list of `int`s
    """
    # convert string values to ints, replacing the empty strings with 0
    int_values = [
        int(n) if n.isdigit() else 0 for row in string_maps for n in row
    ]
    # normalize the integer values to a range of 0 to max_brigtness
    peak = max(int_values)
    normalized_values = [int((n / peak) * max_brightness) for n in int_values]
    return normalized_values


def update_display(led_values: list[int]) -> None:
    """Set the LEDs according to the given values"""
    for index, value in enumerate(led_values):
        y, x = divmod(index, display.width)
        display.pixel(x, y, value)


def randomize(frames: int) -> None:
    """Show a random array on the display for the number of `frames` given"""
    for _ in range(frames):
        for col in range(display.width):
            for row in range(display.height):
                brightness = randrange(0, max_brightness)
                if brightness % 2 == 0:  # skew towards 0
                    brightness = 0
                display.pixel(col, row, brightness)


def mainloop() -> None:
    session = connect()
    last_update_time = 0
    while True:
        if (current_hour := rtc.RTC().datetime.tm_hour) != last_update_time:
            data = get_data(session)
            rows = get_rows(data)
            led_values = normalize_data(rows)
            randomize(16)  # show refresh animation
            update_display(led_values)
            last_update_time = current_hour

        time.sleep(60)


if __name__ == '__main__':
    mainloop()
