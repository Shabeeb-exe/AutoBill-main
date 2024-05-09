#!/usr/bin/python3
from hx711 import HX711
import RPi.GPIO as GPIO  # import GPIO

try:
    hx711 = HX711(
        dout_pin=5,
        pd_sck_pin=18,
        channel='B',
        gain=64
    )

    hx711.reset()   # Before we start, reset the HX711 (not obligate)
    measures = hx711.get_raw_data()
finally:
    GPIO.cleanup()  # always do a GPIO cleanup in your scripts!

print("\n".join(list(map(str,measures))))
