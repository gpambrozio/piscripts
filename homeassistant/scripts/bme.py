#!/usr/bin/env python

import smbus2
import sys
import bme280

port = 1
address = 0x76
bus = smbus2.SMBus(port)

calibration_params = bme280.load_calibration_params(bus, address)

# the sample method will take a single reading and return a
# compensated_reading object
data = bme280.sample(bus, address, calibration_params)

if len(sys.argv) == 1 or sys.argv[1] == "t":
    temperature = round(data.temperature * 9.0 / 5.0, 1) + 32.0
    print('{:.1f}'.format(temperature))
elif sys.argv[1] == "h":
    print('{:.1f}'.format(round(data.humidity, 1)))
else:
    print('{:.1f}'.format(round(data.pressure, 1)))
