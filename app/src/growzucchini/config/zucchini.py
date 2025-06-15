from dataclasses import dataclass, field
from typing import Union

from growzucchini.config.base import BaseConfig


@dataclass(frozen=True)
class Germination:
    TEMP_FLOOR = 24.0
    TEMP_CEIL = 30.0

    HUM_FLOOR = 70.0
    HUM_CEIL = 80.0

    SOIL_MOISTURE_FLOOR = 35.0
    SOIL_MOISTURE_CEIL = 45.0

    SOIL_PH_FLOOR = 6.0
    SOIL_PH_CEIL = 6.8


@dataclass(frozen=True)
class Seedling:
    TEMP_FLOOR = 22.0
    TEMP_CEIL = 28.0

    HUM_FLOOR = 65.0
    HUM_CEIL = 75.0

    SOIL_MOISTURE_FLOOR = 30.0
    SOIL_MOISTURE_CEIL = 40.0

    SOIL_PH_FLOOR = 6.0
    SOIL_PH_CEIL = 6.8


@dataclass(frozen=True)
class Vegetative:
    TEMP_FLOOR = 22.0
    TEMP_CEIL = 28.0

    HUM_FLOOR = 60.0
    HUM_CEIL = 70.0

    SOIL_MOISTURE_FLOOR = 25.0
    SOIL_MOISTURE_CEIL = 35.0

    SOIL_PH_FLOOR = 6.0
    SOIL_PH_CEIL = 7.0


@dataclass(frozen=True)
class Flowering:
    TEMP_FLOOR = 22.0
    TEMP_CEIL = 26.0

    HUM_FLOOR = 50.0
    HUM_CEIL = 60.0

    SOIL_MOISTURE_FLOOR = 25.0
    SOIL_MOISTURE_CEIL = 30.0

    SOIL_PH_FLOOR = 6.0
    SOIL_PH_CEIL = 7.0


@dataclass(frozen=True)
class LateGrowth:
    TEMP_FLOOR = 22.0
    TEMP_CEIL = 26.0

    HUM_FLOOR = 45.0
    HUM_CEIL = 60.0

    SOIL_MOISTURE_FLOOR = 20.0
    SOIL_MOISTURE_CEIL = 30.0

    SOIL_PH_FLOOR = 6.0
    SOIL_PH_CEIL = 7.0


GrowCircleConfigType = Union[Germination, Seedling, Vegetative, Flowering, LateGrowth]


@dataclass
class Zucchini(BaseConfig):
    growth_phase: GrowCircleConfigType = field(default_factory=Germination)
