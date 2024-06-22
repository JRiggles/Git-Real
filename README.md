
# Git Real
#### A hardware-based GitHub contribution graph display

Built with CircuitPython

<img src="images/demo.gif" />

## Hardware
- [Adafruit ESP32 S3 Feather](https://www.adafruit.com/product/5477) (4MB w/ 2MB SRAM version)
- [Adafruit 15x7 CharliePlex LED Matrix Display FeatherWing](https://www.adafruit.com/product/3136) (in green, of course!)
- [Short Female Headers](https://www.adafruit.com/product/2940)
- [Short Male Headers](https://www.adafruit.com/product/3002)

## Software

### Dependecies

This project runs on [CircuitPython 9](https://circuitpython.org/board/adafruit_feather_esp32s3_4mbflash_2mbpsram/) and relies on the following libraries:

- adafruit_bus_device
- adafruit_is31fl3731 (display)
- adafruit_connection_manager
- adafruit_framebuf
- adafruit_ntp
- adafruit_requests

You can download the **lib.zip** file from this repository and copy its contents to the `lib` folder on the `CIRCUITPY` drive if you plan to build one yourself.

### settings.toml

Your `settings.toml` file will need the following items:
```
CIRCUITPY_WIFI_SSID = "<your wifi network name>"
CIRCUITPY_WIFI_PASSWORD = "<your wifi password>"
USERNAME = "<your GitHub username>"
```

## TODO

- [ ] Photos
- [ ] 3D-printable case
- [ ] Battery power and power management stuff?
