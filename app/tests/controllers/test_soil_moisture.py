import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# Assuming SoilMoistureController and its dependencies are structured consistently
# with other controllers, e.g., in app.core or a specific app.growzucchini path.
# For patching, the problem states:
# - `app.growzucchini.controllers.soil_moisture.config.growth_phase`
# - `app.growzucchini.controllers.soil_moisture.get_hardware_config`
# This implies SoilMoistureController is likely in `app.growzucchini.controllers.soil_moisture`.

# Let's assume this structure for the import of the controller itself:
from app.growzucchini.controllers.soil_moisture import SoilMoistureController

# And these are from a common core location:
from app.core.models import SensorData, Control, Action, Device, PhaseConfig
from app.core.device import DEVICE_REGISTRY
from app.core.controller import CONTROLLER_REGISTRY

# Import mock_command_queue fixture (pytest will find it in conftest.py)
# from app.tests.conftest import mock_command_queue


# 1. Mock Configurations
class MockGrowthPhaseConfig(PhaseConfig):
    SOIL_MOISTURE_FLOOR: int = 30

    # Other values to make PhaseConfig concrete, using defaults
    TEMP_LOW: float = 18.0; TEMP_HIGH: float = 30.0; TEMP_MIDDLE: float = 24.0
    HUMIDITY_LOW: float = 40.0; HUMIDITY_HIGH: float = 70.0; HUMIDITY_MIDDLE: float = 55.0
    HUM_CEIL: float = 70.0; HUM_FLOOR: float = 60.0
    LIGHT_ON_HOUR: int = 8; LIGHT_OFF_HOUR: int = 20
    FAN_MIN_SPEED: int = 0; FAN_MAX_SPEED: int = 100
    RPM_TARGET: int = 2000; RPM_TOLERANCE: int = 100; RPM_MAX_SPEED: int = 2500; RPM_MIN_SPEED: int = 1000
    WATER_PUMP_INTERVAL_SECONDS: int = 3600; WATER_PUMP_DURATION_SECONDS: int = 60
    DECISION_INTERVAL_SECONDS: int = 5
    WATER_LEVEL_THRESHOLD: int = 100
    PH_LOW: float = 5.5; PH_HIGH: float = 6.5
    EC_LOW: float = 1.2; EC_HIGH: float = 2.0

MOCK_TEST_GROWTH_CONFIG = MockGrowthPhaseConfig()

MOCK_HARDWARE_CONFIG_RETURN_VALUE = {
    'SoilMoistureSensor': {'UPPER_VALUE': 1000}
    # Add other hardware configs if the controller uses them, otherwise this is fine.
}

# Paths for patching, as specified in the prompt
GROWTH_CONFIG_PATH_TO_PATCH = 'app.growzucchini.controllers.soil_moisture.config.growth_phase'
HARDWARE_CONFIG_PATH_TO_PATCH = 'app.growzucchini.controllers.soil_moisture.get_hardware_config'

@pytest.fixture
def mock_water_pump():
    """Provides a mock water pump device."""
    pump = AsyncMock(spec=Device)
    pump.name = "water_pump"
    pump.device_id = "water_pump"
    yield pump

@pytest.fixture
def soil_moisture_controller_instance(mock_water_pump: AsyncMock):
    """
    Provides an instance of SoilMoistureController with patched configs,
    clean registries, and the mock_water_pump registered.
    """
    # Start patches
    # Patch for get_hardware_config
    patch_get_hardware_config = patch(HARDWARE_CONFIG_PATH_TO_PATCH, return_value=MOCK_HARDWARE_CONFIG_RETURN_VALUE)
    # Patch for growth_phase config
    patch_growth_phase_config = patch(GROWTH_CONFIG_PATH_TO_PATCH, MOCK_TEST_GROWTH_CONFIG)

    mocked_get_hardware_config = patch_get_hardware_config.start()
    mocked_growth_phase_config = patch_growth_phase_config.start()

    DEVICE_REGISTRY.clear()
    CONTROLLER_REGISTRY.clear()

    DEVICE_REGISTRY[mock_water_pump.device_id] = mock_water_pump

    try:
        # Instantiate SoilMoistureController. It might take decision_interval.
        # The actual controller code shows it takes `config_params` which are currently unused.
        # `self.one_percent` is calculated in `__init__`.
        controller = SoilMoistureController(decision_interval=MOCK_TEST_GROWTH_CONFIG.DECISION_INTERVAL_SECONDS)
        CONTROLLER_REGISTRY[controller.name] = controller # Default name 'sm'
        yield controller
    finally:
        # Stop patches and clean up
        patch_get_hardware_config.stop()
        patch_growth_phase_config.stop()

        if controller and controller.name in CONTROLLER_REGISTRY:
            del CONTROLLER_REGISTRY[controller.name]
        if mock_water_pump.device_id in DEVICE_REGISTRY:
            del DEVICE_REGISTRY[mock_water_pump.device_id]

# --- Test Cases ---
# Logic based on prompt:
# one_percent = UPPER_VALUE / 100 = 1000 / 100 = 10.
# Action threshold: normalized_value <= SOIL_MOISTURE_FLOOR - 2
# SOIL_MOISTURE_FLOOR = 30, so threshold is normalized_value <= 28.
# This means raw_sensor_value / one_percent <= 28  => raw_sensor_value / 10 <= 28 => raw_sensor_value <= 280.

@pytest.mark.asyncio
async def test_soil_too_dry_pump_on(soil_moisture_controller_instance: SoilMoistureController, mock_water_pump: AsyncMock, mock_command_queue: asyncio.Queue):
    """Raw sensor 270 -> normalized 27. 27 <= 28, so pump ON."""
    raw_sensor_value = 270
    # Normalized value = 270 / 10 = 27. Target: <= 28.
    control_data = Control(device_id='water_pump', current_value=0) # pin/type arbitrary for this test
    sensor_data = SensorData(sensor='sm', value=raw_sensor_value, controls=[control_data])

    await soil_moisture_controller_instance.execute(sensor_data, sensor_data.controls, mock_command_queue)

    mock_water_pump.set_action.assert_called_once_with(Action.UP)

@pytest.mark.asyncio
async def test_soil_at_threshold_pump_on(soil_moisture_controller_instance: SoilMoistureController, mock_water_pump: AsyncMock, mock_command_queue: asyncio.Queue):
    """Raw sensor 280 -> normalized 28. 28 <= 28, so pump ON."""
    raw_sensor_value = 280
    # Normalized value = 280 / 10 = 28. Target: <= 28.
    control_data = Control(device_id='water_pump', current_value=0)
    sensor_data = SensorData(sensor='sm', value=raw_sensor_value, controls=[control_data])

    await soil_moisture_controller_instance.execute(sensor_data, sensor_data.controls, mock_command_queue)

    mock_water_pump.set_action.assert_called_once_with(Action.UP)

@pytest.mark.asyncio
async def test_soil_moisture_just_above_threshold_pump_off(soil_moisture_controller_instance: SoilMoistureController, mock_water_pump: AsyncMock, mock_command_queue: asyncio.Queue):
    """Raw sensor 281 -> normalized 28.1. 28.1 > 28, so pump OFF."""
    raw_sensor_value = 281
    # Normalized value = 281 / 10 = 28.1. Target: <= 28. This is false.
    control_data = Control(device_id='water_pump', current_value=0)
    sensor_data = SensorData(sensor='sm', value=raw_sensor_value, controls=[control_data])

    await soil_moisture_controller_instance.execute(sensor_data, sensor_data.controls, mock_command_queue)

    mock_water_pump.set_action.assert_not_called()

@pytest.mark.asyncio
async def test_soil_moisture_sufficient_pump_off(soil_moisture_controller_instance: SoilMoistureController, mock_water_pump: AsyncMock, mock_command_queue: asyncio.Queue):
    """Raw sensor 400 -> normalized 40. 40 > 28, so pump OFF."""
    raw_sensor_value = 400
    # Normalized value = 400 / 10 = 40. Target: <= 28. This is false.
    control_data = Control(device_id='water_pump', current_value=0)
    sensor_data = SensorData(sensor='sm', value=raw_sensor_value, controls=[control_data])

    await soil_moisture_controller_instance.execute(sensor_data, sensor_data.controls, mock_command_queue)

    mock_water_pump.set_action.assert_not_called()

# It would also be good to test the decision_interval logic for SoilMoistureController,
# similar to how it was done for TemperatureController, if time permits or if specifically requested.
# For now, these tests cover the core threshold logic.

print("app/tests/controllers/test_soil_moisture.py created.")

```
