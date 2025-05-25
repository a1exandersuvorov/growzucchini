from dataclasses import dataclass, field
from typing import Union

from growzucchini.config.base import BaseConfig


@dataclass(frozen=True)
class Germination:
    TEMP_MIDDLE = 27.0  # 24-30

    HUM_FLOOR = 70
    HUM_CEIL = 80

    SOIL_MOISTURE_FLOOR = 35
    SOIL_MOISTURE_CEIL = 45

    SOIL_PH_FLOOR = 6.0
    SOIL_PH_CEIL = 6.8


@dataclass(frozen=True)
class Seedling:
    TEMP_MIDDLE = 25.0 # 22-28

    HUM_FLOOR = 65
    HUM_CEIL = 75

    SOIL_MOISTURE_FLOOR = 30
    SOIL_MOISTURE_CEIL = 40

    SOIL_PH_FLOOR = 6.0
    SOIL_PH_CEIL = 6.8


@dataclass(frozen=True)
class Vegetative:
    TEMP_MIDDLE = 25.0 # 22-28

    HUM_FLOOR = 60
    HUM_CEIL = 70

    SOIL_MOISTURE_FLOOR = 25
    SOIL_MOISTURE_CEIL = 35

    SOIL_PH_FLOOR = 6.0
    SOIL_PH_CEIL = 7.0


@dataclass(frozen=True)
class Flowering:
    TEMP_MIDDLE = 24.0  # 22-26

    HUM_FLOOR = 50
    HUM_CEIL = 60

    SOIL_MOISTURE_FLOOR = 25
    SOIL_MOISTURE_CEIL = 30

    SOIL_PH_FLOOR = 6.0
    SOIL_PH_CEIL = 7.0


@dataclass(frozen=True)
class LateGrowth:
    TEMP_MIDDLE = 24.0  # 22-26

    HUM_FLOOR = 45
    HUM_CEIL = 60

    SOIL_MOISTURE_FLOOR = 20
    SOIL_MOISTURE_CEIL = 30

    SOIL_PH_FLOOR = 6.0
    SOIL_PH_CEIL = 7.0


GrowCircleConfigType = Union[Germination, Seedling, Vegetative, Flowering, LateGrowth]


@dataclass
class Zucchini(BaseConfig):
    growth_phase: GrowCircleConfigType = field(default_factory=Germination)
