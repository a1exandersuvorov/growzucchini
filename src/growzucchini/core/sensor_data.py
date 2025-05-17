from dataclasses import dataclass
from typing import List

'''
{
  "sensor": "dh",
  "label": "Humidity",
  "value": 78,
  "unit": "%",
  "controls": [
    {"pin": 4, "type": "digital", "device": "alarm_light"},
    {"pin": 5, "type": "digital", "device": "alarm_sound"}
  ]
}
'''

@dataclass
class Control:
    pin: int
    type: str
    device: str

@dataclass
class SensorData:
    sensor: str
    label: str
    value: float
    unit: str
    controls: List[Control]

@dataclass
class State:
    value: float