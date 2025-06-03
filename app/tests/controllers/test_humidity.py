import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# Assuming these are the correct paths to your application's modules
# Adjust the import path for HumidityController and config if it's different.
# The problem states `app.growzucchini.controllers.humidity.config.growth_phase` for config
# and implies HumidityController is in `app.growzucchini.controllers.humidity` or similar.
# For consistency with previous tests, let's assume a flatter structure like app.core
# If `HumidityController` is in `app.growzucchini.controllers.humidity`:
# from app.growzucchini.controllers.humidity import HumidityController
# from app.core.device import DEVICE_REGISTRY # Assuming device and models are in core
# from app.core.models import SensorData, Control, Action, Device, PhaseConfig
# from app.core.controller import CONTROLLER_REGISTRY

# Let's assume a structure similar to TemperatureController for now:
from app.core.controller import HumidityController, CONTROLLER_REGISTRY # Assuming HumidityController is here
from app.core.device import DEVICE_REGISTRY
from app.core.models import SensorData, Control, Action, Device, PhaseConfig

# Import fixtures from conftest.py (pytest will find them automatically)
# from app.tests.conftest import mock_command_queue

# Define a mock growth phase config, similar to test_temperature.py
class MockGrowthPhaseConfig(PhaseConfig):
    # Values from problem description for humidity tests
    HUM_CEIL: float = 70.0
    HUM_FLOOR: float = 60.0

    # Other values to make PhaseConfig concrete, taken from test_temperature.py's example
    TEMP_LOW: float = 18.0
    TEMP_HIGH: float = 30.0
    TEMP_MIDDLE: float = 24.0
    HUMIDITY_LOW: float = 40.0 # General range, HUM_FLOOR/CEIL are specific operational points
    HUMIDITY_HIGH: float = 70.0
    HUMIDITY_MIDDLE: float = 55.0
    LIGHT_ON_HOUR: int = 8
    LIGHT_OFF_HOUR: int = 20
    FAN_MIN_SPEED: int = 0
    FAN_MAX_SPEED: int = 100
    WATER_PUMP_INTERVAL_SECONDS: int = 3600
    WATER_PUMP_DURATION_SECONDS: int = 60
    DECISION_INTERVAL_SECONDS: int = 5 # Default from Controller base class
    WATER_LEVEL_THRESHOLD: int = 100
    PH_LOW: float = 5.5
    PH_HIGH: float = 6.5
    EC_LOW: float = 1.2
    EC_HIGH: float = 2.0

TEST_CONFIG = MockGrowthPhaseConfig()

# Path for patching config. The problem statement suggests:
# `app.growzucchini.controllers.humidity.config.growth_phase`
# This implies HumidityController might be in `app.growzucchini.controllers.humidity.py`
# and that file imports `config` and uses `config.growth_phase`.
# Let's use this path for the patch.
CONFIG_PATH_TO_PATCH = 'app.growzucchini.controllers.humidity.config.growth_phase'
# If HumidityController is in app.core.controller and imports config from app.config:
# CONFIG_PATH_TO_PATCH = 'app.core.controller.config.growth_phase'
# For now, sticking to the problem's specified path. This requires that such a path is valid.

@pytest.fixture
def mock_alarm_light():
    light = AsyncMock(spec=Device)
    light.name = "alarm_light"
    light.device_id = "alarm_light"
    yield light # Registration and cleanup will be handled by humidity_controller_instance

@pytest.fixture
def mock_humidifier():
    humidifier = AsyncMock(spec=Device)
    humidifier.name = "humidifier"
    humidifier.device_id = "humidifier"
    yield humidifier # Registration and cleanup will be handled by humidity_controller_instance

@pytest.fixture
def humidity_controller_instance(mock_alarm_light: AsyncMock, mock_humidifier: AsyncMock):
    """
    Provides an instance of HumidityController with a clean registry state
    and patched config.
    """
    DEVICE_REGISTRY.clear()
    CONTROLLER_REGISTRY.clear()

    DEVICE_REGISTRY[mock_alarm_light.device_id] = mock_alarm_light
    DEVICE_REGISTRY[mock_humidifier.device_id] = mock_humidifier

    # Try to determine the actual import path for config within HumidityController.
    # If HumidityController is in `app.core.controller`, it's more likely to use `app.config.growth_phase`
    # or `app.core.controller.config.growth_phase`.
    # The problem specified `app.growzucchini.controllers.humidity.config.growth_phase`.
    # This implies a specific project structure. Let's assume this is correct.
    # If this patch path is wrong, the tests will fail or not behave as expected.
    try:
        with patch(CONFIG_PATH_TO_PATCH, TEST_CONFIG):
            # Assuming HumidityController takes decision_interval like other controllers
            controller = HumidityController(decision_interval=TEST_CONFIG.DECISION_INTERVAL_SECONDS)
            CONTROLLER_REGISTRY[controller.name] = controller # Default name is 'dh' for HumidityController
            yield controller
    except ModuleNotFoundError:
        # Fallback patch path, more consistent with TemperatureController if HC is in app.core.controller
        fallback_config_path = 'app.core.controller.config.growth_phase'
        print(f"Warning: Could not patch {CONFIG_PATH_TO_PATCH}. Trying {fallback_config_path}.")
        with patch(fallback_config_path, TEST_CONFIG):
            controller = HumidityController(decision_interval=TEST_CONFIG.DECISION_INTERVAL_SECONDS)
            CONTROLLER_REGISTRY[controller.name] = controller
            yield controller


    # Cleanup
    if controller.name in CONTROLLER_REGISTRY:
        del CONTROLLER_REGISTRY[controller.name]
    if mock_alarm_light.device_id in DEVICE_REGISTRY:
        del DEVICE_REGISTRY[mock_alarm_light.device_id]
    if mock_humidifier.device_id in DEVICE_REGISTRY:
        del DEVICE_REGISTRY[mock_humidifier.device_id]

# --- Test Cases ---

@pytest.mark.asyncio
async def test_humidity_too_high(humidity_controller_instance: HumidityController, mock_alarm_light: AsyncMock, mock_humidifier: AsyncMock, mock_command_queue: asyncio.Queue):
    """Test behavior when humidity is too high."""
    humidity_value = TEST_CONFIG.HUM_CEIL + 5  # e.g., 75
    sensor_data = SensorData(
        temperature=25, humidity=humidity_value,
        controls=[
            Control(device_id="alarm_light", current_value=0), # Dummy pin/type
            Control(device_id="humidifier", current_value=0)
        ]
    )

    await humidity_controller_instance.execute(sensor_data, sensor_data.controls, mock_command_queue)

    mock_alarm_light.set_action.assert_called_once_with(Action.DOWN)
    mock_humidifier.set_action.assert_called_once_with(Action.DOWN)

@pytest.mark.asyncio
async def test_humidity_too_low(humidity_controller_instance: HumidityController, mock_alarm_light: AsyncMock, mock_humidifier: AsyncMock, mock_command_queue: asyncio.Queue):
    """Test behavior when humidity is too low."""
    # According to logic: Action.UP if HUM_FLOOR <= val <= HUM_CEIL - 2.
    # If val < HUM_FLOOR, no action is specified for humidifier or alarm_light.
    humidity_value = TEST_CONFIG.HUM_FLOOR - 5  # e.g., 55
    sensor_data = SensorData(
        temperature=25, humidity=humidity_value,
        controls=[
            Control(device_id="alarm_light", current_value=0),
            Control(device_id="humidifier", current_value=0)
        ]
    )

    await humidity_controller_instance.execute(sensor_data, sensor_data.controls, mock_command_queue)

    mock_alarm_light.set_action.assert_not_called()
    mock_humidifier.set_action.assert_not_called()

@pytest.mark.asyncio
async def test_humidity_optimal_for_humidifier_on(humidity_controller_instance: HumidityController, mock_alarm_light: AsyncMock, mock_humidifier: AsyncMock, mock_command_queue: asyncio.Queue):
    """Test behavior for optimal humidity to turn humidifier ON."""
    # HUM_FLOOR <= val <= HUM_CEIL - 2.  (e.g., 60 <= val <= 68)
    # Let's pick 65.
    humidity_value = TEST_CONFIG.HUM_FLOOR + 5  # e.g., 65
    assert TEST_CONFIG.HUM_FLOOR <= humidity_value <= TEST_CONFIG.HUM_CEIL - 2

    sensor_data = SensorData(
        temperature=25, humidity=humidity_value,
        controls=[
            Control(device_id="alarm_light", current_value=0),
            Control(device_id="humidifier", current_value=0) # Assume humidifier is currently off
        ]
    )

    await humidity_controller_instance.execute(sensor_data, sensor_data.controls, mock_command_queue)

    mock_alarm_light.set_action.assert_not_called() # Alarm light not affected in this range
    mock_humidifier.set_action.assert_called_once_with(Action.UP)

@pytest.mark.asyncio
async def test_humidity_slightly_below_ceil_no_action(humidity_controller_instance: HumidityController, mock_alarm_light: AsyncMock, mock_humidifier: AsyncMock, mock_command_queue: asyncio.Queue):
    """Test behavior when humidity is high but not in UP range, and not > CEIL."""
    # val just below HUM_CEIL but above HUM_CEIL - 2. (e.g., 69 if CEIL=70)
    # Logic: Action.UP if val <= HUM_CEIL - 2. So, 69 is not <= 68. No UP action.
    # Logic: Action.DOWN if val > HUM_CEIL. So, 69 is not > 70. No DOWN action.
    # Thus, no action should be taken on humidifier.
    humidity_value = TEST_CONFIG.HUM_CEIL - 1  # e.g., 69
    assert not (TEST_CONFIG.HUM_FLOOR <= humidity_value <= TEST_CONFIG.HUM_CEIL - 2) # Should be false for UP
    assert not (humidity_value > TEST_CONFIG.HUM_CEIL) # Should be false for DOWN

    sensor_data = SensorData(
        temperature=25, humidity=humidity_value,
        controls=[
            Control(device_id="alarm_light", current_value=0),
            Control(device_id="humidifier", current_value=0)
        ]
    )

    await humidity_controller_instance.execute(sensor_data, sensor_data.controls, mock_command_queue)

    mock_alarm_light.set_action.assert_not_called()
    mock_humidifier.set_action.assert_not_called()

# A note on decision_interval for HumidityController:
# These tests do not explicitly check the decision_interval logic for HumidityController
# as test_temperature.py did for TemperatureController. If HumidityController also
# implements such logic (which it should, inheriting from Controller base class),
# similar tests for decision_interval could be added. For now, focusing on the humidity thresholds.

# A note on `SensorData.controls`:
# The `execute` method of the base `Controller` class takes `controls: list[Control]`.
# The `HumidityController.get_actions_for_phase` method also takes `controls`.
# These `Control` objects represent the current state/configuration of devices.
# While the current tests provide them, the `HumidityController` logic described
# (if val > HUM_CEIL then DOWN, if in range then UP) primarily depends on `sensor_data.humidity`
# and doesn't seem to use the `current_value` from `Control` objects for its decisions,
# only for determining which devices to act upon (e.g. "humidifier", "alarm_light").
# The provided `Control` objects with dummy values are sufficient for this.

print("app/tests/controllers/test_humidity.py created.")

```
