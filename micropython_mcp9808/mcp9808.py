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

from micropython import const
from micropython_mcp9808.i2c_helpers import CBits, RegisterStruct


__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/jposada202020/MicroPython_MCP9808.git"


_CONFIG = const(0x01)
_UPPER_TEMP = const(0x02)
_LOWER_TEMP = const(0x02)
_CRITICAL_TEMP = const(0x02)
_TEMP = const(0x05)
_REG_WHOAMI = const(0x07)

HYSTERESIS_0 = const(0b00)
HYSTERESIS_1_5 = const(0b01)
HYSTERESIS_3 = const(0b10)
HYSTERESIS_6 = const(0b11)
hysteresis_values = (HYSTERESIS_0, HYSTERESIS_1_5, HYSTERESIS_3, HYSTERESIS_6)

CONTINUOUS = const(0b00)
SHUTDOWN = const(0b1)
power_mode_values = (CONTINUOUS, SHUTDOWN)


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
    _temperature_upper = CBits(11, _UPPER_TEMP, 2, 2, False)
    _temperature_lower = CBits(11, _LOWER_TEMP, 2, 2, False)
    _temperature_critical = CBits(11, _CRITICAL_TEMP, 2, 2, False)

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
    def temperature(self) -> float:
        """
        Temperature in Celsius
        """
        return self._convert_temperature(self._temperature_data)

    @staticmethod
    def _convert_temperature(temp: int) -> float:

        high_byte = temp >> 8
        low_byte = temp & 0xFF
        if high_byte & 0x10 == 0x10:
            high_byte = high_byte & 0x0F
            return 256 - (high_byte * 16 + low_byte / 16.0)
        return high_byte * 16 + low_byte / 16.0

    @property
    def temperature_upper(self) -> float:
        """
        Upper temperature in Celsius
        """
        return self._convert_temperature(self._temperature_upper)

    @temperature_upper.setter
    def temperature_upper(self, value: int) -> None:
        if not isinstance(value, int):
            raise ValueError("Temperature must be an int value")
        self._temperature_upper = self._limit_temperatures(value)

    @staticmethod
    def _limit_temperatures(temp: int) -> int:
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

        value = high_byte << 8 | low_byte

        return value

    @property
    def temperature_lower(self) -> float:
        """
        Lower temperature in Celsius
        """
        return self._convert_temperature(self._temperature_lower)

    @temperature_lower.setter
    def temperature_lower(self, value: int) -> None:
        if not isinstance(value, int):
            raise ValueError("Temperature must be an int value")
        self._temperature_lower = self._limit_temperatures(value)

    @property
    def temperature_critical(self) -> float:
        """
        Critical temperature in Celsius
        """
        return self._convert_temperature(self._temperature_critical)

    @temperature_critical.setter
    def temperature_critical(self, value: int) -> None:
        if not isinstance(value, int):
            raise ValueError("Temperature must be an int value")
        self._temperature_critical = self._limit_temperatures(value)
