# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT

import time
from machine import Pin, I2C
from micropython_mcp9808 import mcp9808

i2c = I2C(1, sda=Pin(2), scl=Pin(3))  # Correct I2C pins for RP2040
mcp = mcp9808.MCP9808(i2c)

mcp.temperature_lower = 10
mcp.temperature_upper = 25
mcp.temperature_critical = 35

while True:
    print("Temperature: {:.2f}C".format(mcp.temperature))
    alert_status = mcp.alert_status
    if alert_status.high_alert:
        print("Temperature above high set limit!")
    if alert_status.low_alert:
        print("Temperature below low set limit!")
    if alert_status.critical_alert:
        print("Temperature above critical set limit!")
    time.sleep(1)
