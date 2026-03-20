# SPDX-License-Identifier: GPL-3.0-or-later
#
# turing-smart-screen-python - a Python system monitor and library for USB-C displays like Turing Smart Screen or XuanFang
# https://github.com/mathoudebine/turing-smart-screen-python/
#
# Copyright (C) 2021 Matthieu Houdebine (mathoudebine)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# This file allows to add custom data source as sensors and display them in System Monitor themes
# There is no limitation on how much custom data source classes can be added to this file
# See CustomDataExample theme for the theme implementation part

import json
import math
import platform
import subprocess
import time
from abc import ABC, abstractmethod
from typing import List

import psutil
from ping3 import ping

import library.config as config

_SENSORS_CACHE = {"time": 0.0, "data": {}}


def _read_sensors_json():
    now = time.monotonic()
    if now - _SENSORS_CACHE["time"] < 1:
        return _SENSORS_CACHE["data"]

    data = {}
    try:
        output = subprocess.run(
            ["sensors", "-j"],
            capture_output=True,
            text=True,
            check=False,
            timeout=1
        )
        if output.returncode == 0 and output.stdout.strip():
            data = json.loads(output.stdout)
    except Exception:
        data = {}

    _SENSORS_CACHE["time"] = now
    _SENSORS_CACHE["data"] = data
    return data


def _first_chip_value(chip_data, section_prefix, key_suffix):
    for section_name, section_data in chip_data.items():
        if not isinstance(section_data, dict) or not section_name.startswith(section_prefix):
            continue

        for key, value in section_data.items():
            if key.endswith(key_suffix) and isinstance(value, (int, float)):
                return float(value)

    return None


def _nouveau_gpu_metrics():
    for chip_name, chip_data in _read_sensors_json().items():
        if not chip_name.startswith("nouveau-pci-") or not isinstance(chip_data, dict):
            continue

        return {
            "temp": _first_chip_value(chip_data, "temp", "_input"),
            "fan": _first_chip_value(chip_data, "fan", "_input"),
        }

    return {"temp": None, "fan": None}


# Custom data classes must be implemented in this file, inherit the CustomDataSource and implement its 2 methods
class CustomDataSource(ABC):
    @abstractmethod
    def as_numeric(self) -> float:
        # Numeric value will be used for graph and radial progress bars
        # If there is no numeric value, keep this function empty
        pass

    @abstractmethod
    def as_string(self) -> str:
        # Text value will be used for text display and radial progress bar inner text
        # Numeric value can be formatted here to be displayed as expected
        # It is also possible to return a text unrelated to the numeric value
        # If this function is empty, the numeric value will be used as string without formatting
        pass

    @abstractmethod
    def last_values(self) -> List[float]:
        # List of last numeric values will be used for plot graph
        # If you do not want to draw a line graph or if your custom data has no numeric values, keep this function empty
        pass


# Example for a custom data class that has numeric and text values
class ExampleCustomNumericData(CustomDataSource):
    # This list is used to store the last 10 values to display a line graph
    last_val = [math.nan] * 10  # By default, it is filed with math.nan values to indicate there is no data stored

    def as_numeric(self) -> float:
        # Numeric value will be used for graph and radial progress bars
        # Here a Python function from another module can be called to get data
        # Example: self.value = my_module.get_rgb_led_brightness() / audio.system_volume() ...
        self.value = 75.845

        # Store the value to the history list that will be used for line graph
        self.last_val.append(self.value)
        # Also remove the oldest value from history list
        self.last_val.pop(0)

        return self.value

    def as_string(self) -> str:
        # Text value will be used for text display and radial progress bar inner text.
        # Numeric value can be formatted here to be displayed as expected
        # It is also possible to return a text unrelated to the numeric value
        # If this function is empty, the numeric value will be used as string without formatting
        # Example here: format numeric value: add unit as a suffix, and keep 1 digit decimal precision
        return f'{self.value:>5.1f}%'
        # Important note! If your numeric value can vary in size, be sure to display it with a default size.
        # E.g. if your value can range from 0 to 9999, you need to display it with at least 4 characters every time.
        # --> return f'{self.as_numeric():>4}%'
        # Otherwise, part of the previous value can stay displayed ("ghosting") after a refresh

    def last_values(self) -> List[float]:
        # List of last numeric values will be used for plot graph
        return self.last_val


# Example for a custom data class that only has text values
class ExampleCustomTextOnlyData(CustomDataSource):
    def as_numeric(self) -> float:
        # If there is no numeric value, keep this function empty
        pass

    def as_string(self) -> str:
        # If a custom data class only has text values, it won't be possible to display graph or radial bars
        return "Python: " + platform.python_version()

    def last_values(self) -> List[float]:
        # If a custom data class only has text values, it won't be possible to display line graph
        pass


class MeroGpuTemp(CustomDataSource):
    last_val = [math.nan] * 30

    def as_numeric(self) -> float:
        value = _nouveau_gpu_metrics()["temp"]
        self.value = value if value is not None else math.nan

        self.last_val.append(self.value)
        self.last_val.pop(0)

        return self.value

    def as_string(self) -> str:
        if not hasattr(self, "value"):
            self.as_numeric()
        if math.isnan(self.value):
            return "--°C"
        return f"{int(round(self.value))}°C"

    def last_values(self) -> List[float]:
        return self.last_val


class MeroGpuFan(CustomDataSource):
    last_val = [math.nan] * 30

    def as_numeric(self) -> float:
        value = _nouveau_gpu_metrics()["fan"]
        self.value = value if value is not None else math.nan

        self.last_val.append(self.value)
        self.last_val.pop(0)

        return self.value

    def as_string(self) -> str:
        if not hasattr(self, "value"):
            self.as_numeric()
        if math.isnan(self.value):
            return "---- RPM"
        return f"{self.value:>4.0f} RPM"

    def last_values(self) -> List[float]:
        return self.last_val


def _active_net_total_bytes():
    total = 0
    try:
        net_stats = psutil.net_if_stats()
    except Exception:
        net_stats = {}
    counters = psutil.net_io_counters(pernic=True)

    for if_name, counter in counters.items():
        if if_name.startswith("lo"):
            continue
        if if_name in net_stats and not net_stats[if_name].isup:
            continue
        total += counter.bytes_sent + counter.bytes_recv

    return total


def _format_rate(rate):
    units = ["B/s", "K/s", "M/s", "G/s"]
    value = float(rate)
    unit = units[0]

    for next_unit in units:
        unit = next_unit
        if value < 1024 or next_unit == units[-1]:
            break
        value /= 1024

    if unit == "B/s":
        return f"{int(value):>4}{unit}"
    return f"{value:>4.1f}{unit}"


class MeroNetRate(CustomDataSource):
    last_total = None
    last_time = None

    def as_numeric(self) -> float:
        now = time.monotonic()
        total = _active_net_total_bytes()

        if self.__class__.last_total is None or self.__class__.last_time is None:
            self.value = 0.0
        else:
            elapsed = max(now - self.__class__.last_time, 0.001)
            self.value = max(0.0, (total - self.__class__.last_total) / elapsed)

        self.__class__.last_total = total
        self.__class__.last_time = now
        return self.value

    def as_string(self) -> str:
        if not hasattr(self, "value"):
            self.as_numeric()
        return f"NET {_format_rate(self.value)}"

    def last_values(self) -> List[float]:
        return []


class MeroPing(CustomDataSource):
    def as_numeric(self) -> float:
        target = config.CONFIG_DATA["config"].get("PING", "8.8.8.8")
        try:
            value = ping(dest_addr=target, unit="ms", timeout=0.6)
        except Exception:
            value = None
        self.value = float(value) if value is not None else math.nan
        return self.value

    def as_string(self) -> str:
        if not hasattr(self, "value"):
            self.as_numeric()
        if math.isnan(self.value):
            return "PING --"
        return f"PING {int(round(self.value))}ms"

    def last_values(self) -> List[float]:
        return []


class MeroClock(CustomDataSource):
    def as_numeric(self) -> float:
        now = time.localtime()
        self.value = now.tm_hour + now.tm_min / 60.0
        self.display = time.strftime("%I:%M%p", now).lstrip("0")
        return self.value

    def as_string(self) -> str:
        if not hasattr(self, "display"):
            self.as_numeric()
        return self.display

    def last_values(self) -> List[float]:
        return []
