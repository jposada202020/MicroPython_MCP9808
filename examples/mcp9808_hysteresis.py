# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT

import time
from machine import Pin, I2C
from micropython_mcp9808 import mcp9808

i2c = I2C(1, sda=Pin(2), scl=Pin(3))  # Correct I2C pins for RP2040
mcp = mcp9808.MCP9808(i2c)

mcp.hysteresis = mcp9808.HYSTERESIS_0

while True:
    for hysteresis in mcp9808.hysteresis_values:
        print("Current Hysteresis setting: ", mcp.hysteresis)
        for _ in range(10):
            temp = mcp.temperature
            print("Temperature: {:.2f}C".format(temp))
            time.sleep(0.5)
