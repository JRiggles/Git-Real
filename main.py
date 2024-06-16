import adafruit_requests
import board
import busio
import os
import socketpool
import ssl
import wifi
from adafruit_is31fl3731.charlie_wing import CharlieWing

# TODO: get IS31FL3731 Library
# TODO: update every x hours
# TODO: battery power? (+ power management)
# IDEA: lower max_brightness when on battery power

BASE_URL = 'https://github-contributions-api.deno.dev/'
USERNAME = os.getenv('USERNAME')
RESPONSE_TYPE = '.text'

# https://learn.adafruit.com/adafruit-15x7-7x15-charlieplex-led-matrix-charliewing-featherwing

i2c = busio.I2C(board.SCL, board.SDA)
display = CharlieWing(i2c)
max_brightness = 255


def connect() -> None:  # FIXME: typing
    """Connect to WiFI and return a `Session` object"""
    wifi.radio.connect(os.getenv('WIFI_SSID'), os.getenv('WIFI_PASSWORD'))
    pool = socketpool.SocketPool(wifi.radio)
    session = adafruit_requests.Session(pool, ssl.create_default_context())
    return session


def get_data(session) -> str:  # FIXME: typing
    """Get GitHub contribution data string"""
    response = session.get(BASE_URL + USERNAME + RESPONSE_TYPE)
    if (status := response.status_code) == 200:
        return response.content
    else:
        return str(status)


def get_rows(data: str) -> list[map]:
    # split response content into rows, removing the contribution count at the
    # beginning and the empty cell at the end
    rows = data.decode().split('\n')[1:-1]
    # split the rows into maps of strings, keeping the last 'display.width'
    # elements
    string_values = [
        map(str.strip, row.split(',')[-display.width:]) for row in rows
    ]
    return string_values


def normalize_data(string_values: list[map]) -> list[int]:
    """
    Normalize the values in the contribution data string to a range of
    `0` to `max_brightness` and return them as a list of `int`s
    """
    # convert string values to ints, replacing the empty strings with 0
    int_values = [
        int(n) if n.isdigit() else 0 for row in string_values for n in row
    ]
    # normalize the integer values to a range of 0 to max_brigtness
    peak = max(int_values)
    normalized_values = [int((n / peak) * max_brightness) for n in int_values]
    return normalized_values


def update_display(led_values: list[int]) -> None:
    """Set the LEDs according to the given values"""
    for index, value in enumerate(led_values):
        x, y = divmod(index, display.width)
        display.pixel(x, y, value)


if __name__ == '__main__':
    session = connect()
    data = get_data(session)
    rows = get_rows(data)
    led_values = normalize_data(data)
    update_display(led_values)
