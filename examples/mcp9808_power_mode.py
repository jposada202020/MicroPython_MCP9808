# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT

import time
from machine import Pin, I2C
from micropython_mcp9808 import mcp9808

i2c = I2C(1, sda=Pin(2), scl=Pin(3))  # Correct I2C pins for RP2040
mcp = mcp9808.MCP9808(i2c)

mcp.power_mode = mcp9808.SHUTDOWN

while True:
    for power_mode in mcp9808.power_mode_values:
        print("Current Power mode setting: ", mcp.power_mode)
        for _ in range(10):
            print(f"Temperature: {mcp.temperature:.2f}°C")
            print()
            time.sleep(0.5)
        mcp.power_mode = power_mode
