from dataclasses import dataclass


class BaseDevice:
    pass


@dataclass(frozen=True)
class CirculationFan(BaseDevice):
    FAN_SPEED_FLOOR = 800
    FAN_SPEED_CEIL = 1200


@dataclass(frozen=True)
class ExhaustFan(BaseDevice):
    FAN_SPEED_FLOOR = 1000


@dataclass
class Humidifier(BaseDevice):
    f = ""


@dataclass
class WaterPump(BaseDevice):
    f = ""
