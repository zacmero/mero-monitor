"""Run with python3 -m unittest discover -s tests."""
import ast
import math
import unittest
from pathlib import Path
from types import SimpleNamespace
from typing import List


class CpuFanTest(unittest.TestCase):
    def test_selection_and_missing_sensor(self):
        source = Path("overrides/library/sensors/sensors_custom.py").read_text()
        node = next(n for n in ast.parse(source).body
                    if isinstance(n, ast.ClassDef) and n.name == "MeroCpuFan")
        config = SimpleNamespace(CONFIG_DATA={"config": {"CPU_FAN": "AUTO"}})
        fans = {"chip": [SimpleNamespace(label="case", current=700),
                         SimpleNamespace(label="CPU", current=1200)]}
        namespace = dict(math=math, List=List, CustomDataSource=object,
                         config=config, psutil=SimpleNamespace(sensors_fans=lambda: fans))
        exec(compile(ast.Module(body=[node], type_ignores=[]), "sensor", "exec"), namespace)
        sensor = namespace["MeroCpuFan"]()
        self.assertEqual(sensor.as_numeric(), 1200)
        self.assertEqual(sensor.as_string(), "1200")
        config.CONFIG_DATA["config"]["CPU_FAN"] = "chip/case"
        self.assertEqual(sensor.as_numeric(), 700)
        config.CONFIG_DATA["config"]["CPU_FAN"] = "missing/fan"
        self.assertTrue(math.isnan(sensor.as_numeric()))
        self.assertEqual(sensor.as_string(), "--")
        fans.clear()
        self.assertTrue(math.isnan(sensor.as_numeric()))
        self.assertEqual(sensor.as_string(), "--")
        fans["it8620"] = [SimpleNamespace(label="", current=2257)]
        config.CONFIG_DATA["config"]["CPU_FAN"] = "it8620/fan1"
        self.assertEqual(sensor.as_numeric(), 2257)
        self.assertEqual(sensor.as_string(), "2257")
