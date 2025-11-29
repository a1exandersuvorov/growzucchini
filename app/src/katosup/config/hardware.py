from dataclasses import dataclass


class Hardware:
    pass


@dataclass(frozen=True)
class CirculationFan(Hardware):
    FAN_SPEED_FLOOR = 800  # rpm
    FAN_SPEED_CEIL = 1200


@dataclass(frozen=True)
class ExhaustFan(Hardware):
    FAN_SPEED_FLOOR = 1000  # rpm


@dataclass(frozen=True)
class SoilMoistureSensor(Hardware):
    # Upper measurement value or 100% moisture
    UPPER_VALUE = 1023

@dataclass(frozen=True)
class WaterPump(Hardware):
    FLOW_RATE = 2.5 / 60  # l/s
    POT_VOLUME = 2.0  # l
