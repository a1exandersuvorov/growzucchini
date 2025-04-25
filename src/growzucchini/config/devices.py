from dataclasses import dataclass


class BaseDevice:
    pass

@dataclass
class CirculationFan(BaseDevice):
    f = ""


@dataclass
class ExhaustFan(BaseDevice):
    FAN_SPEED_FLOOR = 200
    FAN_SPEED_CEIL = 1800


@dataclass
class Humidifier(BaseDevice):
    f = ""


@dataclass
class WaterPump(BaseDevice):
    f = ""

