# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT

import time
from machine import Pin, I2C
from micropython_mcp9808 import mcp9808

i2c = I2C(1, sda=Pin(2), scl=Pin(3))  # Correct I2C pins for RP2040
mcp = mcp9808.MCP9808(i2c)

mcp.temperature_resolution = mcp9808.RESOLUTION_0_625_C

while True:
    for temperature_resolution in mcp9808.temperature_resolution_values:
        print("Current Temperature resolution setting: ", mcp.temperature_resolution)
        for _ in range(10):
            temp = mcp.temperature
            print("Temperature: {:.2f}C".format(temp))
            time.sleep(0.5)
        mcp.temperature_resolution = temperature_resolution
