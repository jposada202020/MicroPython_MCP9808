# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT

import time
from machine import Pin, I2C
from micropython_mcp9808 import mcp9808

i2c = I2C(1, sda=Pin(2), scl=Pin(3))  # Correct I2C pins for RP2040
mcp = mcp9808.MCP9808(i2c)

print(mcp.temperature_upper)
mcp.temperature_upper = 21
print(mcp.temperature_upper)
# while True:
#     temp = mcp.temperature
#     print("Temperature: {:.2f}C".format(temp))
#     time.sleep(0.5)
