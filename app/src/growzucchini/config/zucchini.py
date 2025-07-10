from dataclasses import dataclass, field
from typing import Union

from growzucchini.config.base import BaseConfig


from typing import Optional

@dataclass(frozen=True)
class Germination:
    TEMP_FLOOR = 24.0
    TEMP_CEIL = 30.0
    NIGHT_TEMP_FLOOR: Optional[float] = None
    NIGHT_TEMP_CEIL: Optional[float] = None

    HUM_FLOOR = 70.0
    HUM_CEIL = 80.0
    # Example for humidity as well, can be added to others if needed
    NIGHT_HUM_FLOOR: Optional[float] = None
    NIGHT_HUM_CEIL: Optional[float] = None

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
    # growth_phase: GrowCircleConfigType = field(default_factory=Germination) # Removed

    def __post_init__(self):
        # Call the BaseConfig's method to set the initial phase
        initial_phase_cls = Germination # Default initial phase
        # Check if BaseConfig's __init__ was called, if not, call it.
        # However, since Zucchini is a dataclass and BaseConfig is its superclass (also a dataclass),
        # super().__init__() is implicitly called if Zucchini doesn't define its own __init__.
        # If BaseConfig's __init__ needs args, Zucchini's __init__ would need to supply them.
        # For now, assuming BaseConfig.__init__() takes no args or is handled by dataclass inheritance.

        # We need to ensure that _actual_growth_phase in BaseConfig is initialized.
        # If BaseConfig's __init__ doesn't run or doesn't initialize _actual_growth_phase,
        # this call might fail or the proxy might be created with a None actual_phase.
        # The __init__ added to BaseConfig sets _actual_growth_phase to None.
        # switch_growth_phase will then correctly set it.
        self.switch_growth_phase(initial_phase_cls)
