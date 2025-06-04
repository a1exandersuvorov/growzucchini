from dataclasses import dataclass


class Hardware:
    pass


@dataclass(frozen=True)
class CirculationFan(Hardware):
    FAN_SPEED_FLOOR = 800
    FAN_SPEED_CEIL = 1200


@dataclass(frozen=True)
class ExhaustFan(Hardware):
    FAN_SPEED_FLOOR = 1000


@dataclass(frozen=True)
class SoilMoistureSensor(Hardware):
    # Upper measurement value or 100% moisture
    UPPER_VALUE = 1023
