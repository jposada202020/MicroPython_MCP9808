# SPDX-FileCopyrightText: 2017 Scott Shawcroft for Adafruit Industries
# SPDX-FileCopyrightText: 2021 Jose David Montoya
# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT
"""
`mcp9808`
================================================================================

MicroPython Driver for the Microchip MCP9808 Temperature Sensor


* Author(s): Jose D. Montoya


"""

from collections import namedtuple
from micropython import const
from micropython_mcp9808.i2c_helpers import CBits, RegisterStruct


__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/jposada202020/MicroPython_MCP9808.git"


_CONFIG = const(0x01)
_UPPER_TEMP = const(0x02)
_LOWER_TEMP = const(0x03)
_CRITICAL_TEMP = const(0x04)
_TEMP = const(0x05)
_REG_WHOAMI = const(0x07)
_RESOLUTION = const(0x08)

HYSTERESIS_0 = const(0b00)
HYSTERESIS_1_5 = const(0b01)
HYSTERESIS_3 = const(0b10)
HYSTERESIS_6 = const(0b11)
hysteresis_values = (HYSTERESIS_0, HYSTERESIS_1_5, HYSTERESIS_3, HYSTERESIS_6)

CONTINUOUS = const(0b00)
SHUTDOWN = const(0b1)
power_mode_values = (CONTINUOUS, SHUTDOWN)

RESOLUTION_0_5_C = const(0b00)
RESOLUTION_0_625_C = const(0b01)
RESOLUTION_0_125_C = const(0b10)
RESOLUTION_0_0625_C = const(0b11)
temperature_resolution_values = (
    RESOLUTION_0_5_C,
    RESOLUTION_0_625_C,
    RESOLUTION_0_125_C,
    RESOLUTION_0_0625_C,
)

AlertStatus = namedtuple("AlertStatus", ["high_alert", "low_alert", "critical_alert"])


class MCP9808:
    """Driver for the MCP9808 Sensor connected over I2C.

    :param ~machine.I2C i2c: The I2C bus the MCP9808 is connected to.
    :param int address: The I2C device address. Defaults to :const:`0x18`

    :raises RuntimeError: if the sensor is not found

    **Quickstart: Importing and using the device**

    Here is an example of using the :class:`MCP9808` class.
    First you will need to import the libraries to use the sensor

    .. code-block:: python

        from machine import Pin, I2C
        from micropython_mcp9808 import mcp9808

    Once this is done you can define your `machine.I2C` object and define your sensor object

    .. code-block:: python

        i2c = I2C(1, sda=Pin(2), scl=Pin(3))
        mcp = mcp9808.MCP9808(i2c)

    Now you have access to the attributes

    .. code-block:: python

        temp = mcp.temperature

    """

    _device_id = RegisterStruct(_REG_WHOAMI, "B")
    _config = RegisterStruct(_CONFIG, "H")

    _hysteresis = CBits(2, _CONFIG, 9, 2, False)
    _power_mode = CBits(1, _CONFIG, 8, 2, False)

    _temperature_data = CBits(13, _TEMP, 0, 2, False)
    _temperature_resolution = CBits(2, _RESOLUTION, 0)

    critical_alert = CBits(1, _TEMP, 7, register_width=1)
    high_alert = CBits(1, _TEMP, 6, register_width=1)
    low_alert = CBits(1, _TEMP, 5, register_width=1)

    def __init__(self, i2c, address: int = 0x18) -> None:
        self._i2c = i2c
        self._address = address

        if self._device_id != 0x04:
            raise RuntimeError("Failed to find MCP9808")

    @property
    def hysteresis(self) -> str:
        """
        Sensor hysteresis

        +------------------------------------+------------------+
        | Mode                               | Value            |
        +====================================+==================+
        | :py:const:`mcp9808.HYSTERESIS_0`   | :py:const:`0b00` |
        +------------------------------------+------------------+
        | :py:const:`mcp9808.HYSTERESIS_1_5` | :py:const:`0b01` |
        +------------------------------------+------------------+
        | :py:const:`mcp9808.HYSTERESIS_3`   | :py:const:`0b10` |
        +------------------------------------+------------------+
        | :py:const:`mcp9808.HYSTERESIS_6`   | :py:const:`0b11` |
        +------------------------------------+------------------+
        """
        values = ("HYSTERESIS_0", "HYSTERESIS_1_5", "HYSTERESIS_3", "HYSTERESIS_6")
        return values[self._hysteresis]

    @hysteresis.setter
    def hysteresis(self, value: int) -> None:
        if value not in hysteresis_values:
            raise ValueError("Value must be a valid hysteresis setting")
        self._hysteresis = value

    @property
    def power_mode(self) -> str:
        """
        Sensor power_mode
        In shutdown, all power-consuming activities are disabled, though
        all registers can be written to or read.  This bit cannot be set
        to ‘1’ when either of the Lock bits is set (bit 6 and bit 7).
        However, it can be cleared to ‘0’ for continuous conversion while
        locked

        +--------------------------------+------------------+
        | Mode                           | Value            |
        +================================+==================+
        | :py:const:`mcp9808.CONTINUOUS` | :py:const:`0b00` |
        +--------------------------------+------------------+
        | :py:const:`mcp9808.SHUTDOWN`   | :py:const:`0b1`  |
        +--------------------------------+------------------+
        """
        values = ("CONTINUOUS", "SHUTDOWN")
        return values[self._power_mode]

    @power_mode.setter
    def power_mode(self, value: int) -> None:
        if value not in power_mode_values:
            raise ValueError("Value must be a valid power_mode setting")
        self._power_mode = value

    @property
    def temperature(self):
        """
        Temperature in Celsius
        """
        data = bytearray(2)
        self._i2c.readfrom_mem_into(self._address, _TEMP, data)

        return self._convert_temperature(data)

    @staticmethod
    def _convert_temperature(temp: bytearray) -> float:

        temp[0] = temp[0] & 0x1F
        if temp[0] & 0x10 == 0x10:
            temp[0] = temp[0] & 0x0F
            return (temp[0] * 16 + temp[1] / 16.0) - 256
        return temp[0] * 16 + temp[1] / 16.0

    @property
    def temperature_upper(self) -> float:
        """
        Upper temperature in Celsius
        """
        return self._get_temperature(_UPPER_TEMP)

    @temperature_upper.setter
    def temperature_upper(self, value: int) -> None:
        if not isinstance(value, int):
            raise ValueError("Temperature must be an int value")
        self._limit_temperatures(value, _UPPER_TEMP)

    def _get_temperature(self, register_address):

        data = bytearray(2)
        self._i2c.readfrom_mem_into(self._address, register_address, data)

        return self._convert_temperature(data)

    def _limit_temperatures(self, temp: int, register_address):
        """Internal function to setup limit temperature
        :param int temp: temperature limit
        """

        if temp < 0:
            negative = True
            temp = abs(temp)
        else:
            negative = False

        high_byte = temp >> 4
        if negative:
            high_byte = high_byte | 0x10

        low_byte = (temp & 0x0F) << 4

        self._i2c.writeto_mem(
            self._address, register_address, bytes([high_byte, low_byte])
        )

    @property
    def temperature_lower(self) -> float:
        """
        Lower temperature in Celsius
        """
        return self._get_temperature(_LOWER_TEMP)

    @temperature_lower.setter
    def temperature_lower(self, value: int) -> None:
        if not isinstance(value, int):
            raise ValueError("Temperature must be an int value")
        self._limit_temperatures(value, _LOWER_TEMP)

    @property
    def temperature_critical(self) -> float:
        """
        Critical temperature in Celsius
        """
        return self._get_temperature(_CRITICAL_TEMP)

    @temperature_critical.setter
    def temperature_critical(self, value: int) -> None:
        if not isinstance(value, int):
            raise ValueError("Temperature must be an int value")
        self._limit_temperatures(value, _CRITICAL_TEMP)

    @property
    def alert_status(self):
        """The current triggered status of the high and low temperature alerts as a AlertStatus
        named tuple with attributes for the triggered status of each alert.

        .. code-block :: python

            import time
            from machine import Pin, I2C
            from micropython_mcp9808 import mcp9808

            i2c = I2C(1, sda=Pin(2), scl=Pin(3))  # Correct I2C pins for RP2040
            mcp = mcp9808.MCP9808(i2c)

            mcp.temperature_lower = 20
            mcp.temperature_upper = 23
            mcp.temperature_critical = 30

            print("High limit: {}".format(mcp.temperature_upper))
            print("Low limit: {}".format(mcp.temperature_lower))
            print("Critical limit: {}".format(mcp.temperature_critical))

            while True:
                print("Temperature: {:.2f}C".format(mcp.temperature))
                alert_status = tmp.alert_status
                if alert_status.high_alert:
                    print("Temperature above high set limit!")
                if alert_status.low_alert:
                    print("Temperature below low set limit!")
                if alert_status.critical_alert:
                    print("Temperature above critical set limit!")
                time.sleep(1)

        """

        return AlertStatus(
            high_alert=self.high_alert,
            low_alert=self.low_alert,
            critical_alert=self.critical_alert,
        )

    @property
    def temperature_resolution(self) -> str:
        """
        Sensor temperature_resolution

        +------------------------------------------+---------------------------+
        | Mode                                     | Value                     |
        +==========================================+===========================+
        | :py:const:`mcp9808.RESOLUTION_0_5_C`     | :py:const:`0b00` 0.5°C    |
        +------------------------------------------+---------------------------+
        | :py:const:`mcp9808.RESOLUTION_0_625_C`   | :py:const:`0b01` 0.25°C   |
        +------------------------------------------+---------------------------+
        | :py:const:`mcp9808.RESOLUTION_0_125_C`   | :py:const:`0b10` 0.125°C  |
        +------------------------------------------+---------------------------+
        | :py:const:`mcp9808.RESOLUTION_0_0625_C`  | :py:const:`0b11` 0.0625°C |
        +------------------------------------------+---------------------------+
        """
        values = (
            "RESOLUTION_0_5_C",
            "RESOLUTION_0_625_C",
            "RESOLUTION_0_125_C",
            "RESOLUTION_0_0625_C",
        )
        return values[self._temperature_resolution]

    @temperature_resolution.setter
    def temperature_resolution(self, value: int) -> None:
        if value not in temperature_resolution_values:
            raise ValueError("Value must be a valid temperature_resolution setting")
        self._temperature_resolution = value
