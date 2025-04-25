from dataclasses import dataclass, field
from typing import Union

from growzucchini.config.base import BaseConfig


@dataclass
class Germination:
    TEMP_FLOOR = 24
    TEMP_CEIL = 30

    HUM_FLOOR = 70
    HUM_CEIL = 80

    SOIL_MOISTURE_FLOOR = 35
    SOIL_MOISTURE_CEIL = 45

    SOIL_PH_FLOOR = 6.0
    SOIL_PH_CEIL = 6.8


@dataclass
class Seedling:
    TEMP_FLOOR = 22
    TEMP_CEIL = 28

    HUM_FLOOR = 65
    HUM_CEIL = 75

    SOIL_MOISTURE_FLOOR = 30
    SOIL_MOISTURE_CEIL = 40

    SOIL_PH_FLOOR = 6.0
    SOIL_PH_CEIL = 6.8


@dataclass
class Vegetative:
    TEMP_FLOOR = 22
    TEMP_CEIL = 28

    HUM_FLOOR = 60
    HUM_CEIL = 70

    SOIL_MOISTURE_FLOOR = 25
    SOIL_MOISTURE_CEIL = 35

    SOIL_PH_FLOOR = 6.0
    SOIL_PH_CEIL = 7.0


@dataclass
class Flowering:
    TEMP_FLOOR = 22
    TEMP_CEIL = 26

    HUM_FLOOR = 50
    HUM_CEIL = 60

    SOIL_MOISTURE_FLOOR = 25
    SOIL_MOISTURE_CEIL = 30

    SOIL_PH_FLOOR = 6.0
    SOIL_PH_CEIL = 7.0


@dataclass
class LateGrowth:
    TEMP_FLOOR = 22
    TEMP_CEIL = 26

    HUM_FLOOR = 45
    HUM_CEIL = 60

    SOIL_MOISTURE_FLOOR = 20
    SOIL_MOISTURE_CEIL = 30

    SOIL_PH_FLOOR = 6.0
    SOIL_PH_CEIL = 7.0


GrowCircleConfigType = Union[Germination, Seedling, Vegetative, Flowering, LateGrowth]


@dataclass
class Zucchini(BaseConfig):
    active_mode: GrowCircleConfigType = field(default_factory=Germination)
