import asyncio
import pytest
import time
from unittest.mock import AsyncMock, MagicMock, patch

# Assuming these are the correct paths to your application's modules
from app.core.controller import TemperatureController, CONTROLLER_REGISTRY
from app.core.device import DEVICE_REGISTRY
from app.core.models import SensorData, Control, Action, Device, PhaseConfig

# Import fixtures from conftest.py (pytest will find them automatically)
# from app.tests.conftest import mock_command_queue, mock_serial_connection_manager # Not directly used here but good to note

# Default configuration values (replace with actual config loading if necessary)
# These values would typically come from a config file or environment variables.
# For testing, we can define them here or mock the config object if the controller uses one.

class MockGrowthPhaseConfig(PhaseConfig):
    TEMP_LOW: float = 18.0
    TEMP_HIGH: float = 30.0
    TEMP_MIDDLE: float = 24.0
    HUMIDITY_LOW: float = 40.0
    HUMIDITY_HIGH: float = 70.0
    HUMIDITY_MIDDLE: float = 55.0
    LIGHT_ON_HOUR: int = 8
    LIGHT_OFF_HOUR: int = 20
    FAN_MIN_SPEED: int = 0
    FAN_MAX_SPEED: int = 100
    WATER_PUMP_INTERVAL_SECONDS: int = 3600  # 1 hour
    WATER_PUMP_DURATION_SECONDS: int = 60    # 1 minute
    DECISION_INTERVAL_SECONDS: int = 5 # Default from Controller base class
    WATER_LEVEL_THRESHOLD: int = 100 # Example value
    PH_LOW: float = 5.5
    PH_HIGH: float = 6.5
    EC_LOW: float = 1.2
    EC_HIGH: float = 2.0


# Using a fixed config for tests
TEST_CONFIG = MockGrowthPhaseConfig()
TEMPERATURE_TOLERANCE = 2.0 # Example tolerance, adjust if defined elsewhere

@pytest.fixture
def mock_exhaust_fan():
    """Provides a mock exhaust fan device."""
    fan = AsyncMock(spec=Device) # Using Device as a base for spec
    fan.name = "exhaust_fan"
    fan.device_id = "exhaust_fan"
    # Register this mock device in the DEVICE_REGISTRY for tests
    DEVICE_REGISTRY[fan.device_id] = fan
    yield fan
    # Clean up: remove the mock device after the test
    if fan.device_id in DEVICE_REGISTRY:
        del DEVICE_REGISTRY[fan.device_id]

@pytest.fixture
def temperature_controller_instance(mock_exhaust_fan): # Depends on mock_exhaust_fan to ensure it's registered
    """
    Provides an instance of TemperatureController with a clean registry state.
    """
    # Clear registries to ensure test isolation
    DEVICE_REGISTRY.clear()
    CONTROLLER_REGISTRY.clear()

    # Re-register the mock fan needed for this controller's tests
    DEVICE_REGISTRY[mock_exhaust_fan.device_id] = mock_exhaust_fan

    # Create and register the controller
    # The TemperatureController might take the config directly or load it globally.
    # Assuming it can be instantiated without explicit config if it uses a global one,
    # or modify instantiation if it requires config passed in.
    # For this example, let's assume TemperatureController uses a global config
    # or has default values that match our TEST_CONFIG for thresholds.
    # If TemperatureController expects config, it should be: TemperatureController(config=TEST_CONFIG)

    # Patching the config used by the controller if it's module-level
    # For this setup, we assume TemperatureController will internally access `app.config.growth_phase`
    # So we patch that location.
    with patch('app.core.controller.config.growth_phase', TEST_CONFIG):
        controller = TemperatureController(decision_interval=TEST_CONFIG.DECISION_INTERVAL_SECONDS) # Pass interval
        CONTROLLER_REGISTRY[controller.name] = controller
        yield controller

    # Clean up controller registry after test
    if controller.name in CONTROLLER_REGISTRY:
        del CONTROLLER_REGISTRY[controller.name]
    # DEVICE_REGISTRY cleanup is handled by mock_exhaust_fan fixture

# --- Test Cases ---

@pytest.mark.asyncio
async def test_temperature_too_high(temperature_controller_instance: TemperatureController, mock_exhaust_fan: AsyncMock, mock_command_queue: asyncio.Queue):
    """Test that the exhaust fan is turned DOWN when temperature is too high."""
    temp_value = TEST_CONFIG.TEMP_MIDDLE + TEMPERATURE_TOLERANCE + 5  # Significantly above
    sensor_data = SensorData(temperature=temp_value, humidity=50) # humidity is arbitrary here

    # Define the control for the exhaust fan that the controller is expected to manage
    exhaust_control = Control(device_id="exhaust_fan", current_value=0) # current_value is arbitrary for this test

    await temperature_controller_instance.execute(sensor_data, [exhaust_control], mock_command_queue)

    mock_exhaust_fan.set_action.assert_called_once_with(Action.DOWN)

@pytest.mark.asyncio
async def test_temperature_too_low(temperature_controller_instance: TemperatureController, mock_exhaust_fan: AsyncMock, mock_command_queue: asyncio.Queue):
    """Test that the exhaust fan is turned UP (or OFF) when temperature is too low."""
    # Current logic for TemperatureController turns fan OFF (Action.UP can mean off for a cooling fan)
    # if temp is low, to stop cooling. If it were a heater, Action.UP would be to turn it on.
    # For an exhaust fan primarily used for cooling, reducing its speed or turning it off (Action.UP if speed=0)
    # is the logical step if temperature is too low.
    temp_value = TEST_CONFIG.TEMP_MIDDLE - TEMPERATURE_TOLERANCE - 5  # Significantly below
    sensor_data = SensorData(temperature=temp_value, humidity=50)
    exhaust_control = Control(device_id="exhaust_fan", current_value=100) # Assume it's running

    await temperature_controller_instance.execute(sensor_data, [exhaust_control], mock_command_queue)

    # Based on TemperatureController logic:
    # if temp < TEMP_MIDDLE - self.tolerance:
    #   actions.append({"device_id": "exhaust_fan", "action": Action.UP}) # UP means turn off/reduce (less cooling)
    mock_exhaust_fan.set_action.assert_called_once_with(Action.UP)

@pytest.mark.asyncio
async def test_temperature_in_range(temperature_controller_instance: TemperatureController, mock_exhaust_fan: AsyncMock, mock_command_queue: asyncio.Queue):
    """Test that the exhaust fan is not activated if temperature is within range."""
    temp_value = TEST_CONFIG.TEMP_MIDDLE # Exactly in the middle
    sensor_data = SensorData(temperature=temp_value, humidity=50)
    exhaust_control = Control(device_id="exhaust_fan", current_value=50) # Some arbitrary current state

    await temperature_controller_instance.execute(sensor_data, [exhaust_control], mock_command_queue)

    mock_exhaust_fan.set_action.assert_not_called()

@pytest.mark.asyncio
async def test_decision_interval(temperature_controller_instance: TemperatureController, mock_exhaust_fan: AsyncMock, mock_command_queue: asyncio.Queue):
    """Test that decisions are not made more frequently than the decision_interval."""
    temp_value_high = TEST_CONFIG.TEMP_MIDDLE + TEMPERATURE_TOLERANCE + 5
    sensor_data_high = SensorData(temperature=temp_value_high, humidity=50)
    exhaust_control = Control(device_id="exhaust_fan", current_value=0)

    # 1. First call - should trigger action
    await temperature_controller_instance.execute(sensor_data_high, [exhaust_control], mock_command_queue)
    mock_exhaust_fan.set_action.assert_called_once_with(Action.DOWN)

    # Reset mock for next assertion, but keep its call count for overall check if needed
    # For this test, we check calls per specific phase.
    mock_exhaust_fan.set_action.reset_mock()

    # 2. Immediate second call - should NOT trigger action due to interval
    await temperature_controller_instance.execute(sensor_data_high, [exhaust_control], mock_command_queue)
    mock_exhaust_fan.set_action.assert_not_called()

    # 3. Wait for decision_interval to pass and call again
    # We need to control time for this test. We can patch time.monotonic.
    # The Controller class uses time.monotonic().
    # The decision_interval for TemperatureController is set from TEST_CONFIG.DECISION_INTERVAL_SECONDS

    # current_time = time.monotonic()
    # with patch('time.monotonic', return_value=current_time + temperature_controller_instance.decision_interval + 1):
    # Using asyncio.sleep for simplicity if direct time manipulation isn't strictly necessary
    # for the controller's internal logic beyond just checking the interval.
    # However, patching time.monotonic is more robust for testing timing logic.

    # Let's refine the time patching for precision.
    # The controller stores `self.last_decision_time`.

    # Simulate time passing by advancing the controller's last_decision_time attribute directly (less ideal)
    # or by patching time.monotonic. Patching is cleaner.

    # Get initial time.monotonic() value as perceived by controller on first call
    # This requires the controller to have been run once.
    # The `last_decision_time` is set *after* a decision is made.

    # To ensure the interval check is effective, we simulate that `decision_interval` seconds have passed.
    # The controller's logic is: `if current_time - self.last_decision_time[key] < self.decision_interval:`

    # We will patch `time.monotonic` used by the controller.
    # Assume `app.core.controller.time` is where `time.monotonic` is called.
    # If it's just `import time; time.monotonic()`, then patch `'time.monotonic'`.

    # First call already happened and set_action was called once.
    # last_decision_time for "exhaust_fan_temp" is now set.

    # Patch time.monotonic to simulate time advancement
    # The TemperatureController uses a key like f"{device_id}_temp"
    decision_key = "exhaust_fan_temp"
    assert decision_key in temperature_controller_instance.last_decision_time
    original_last_decision_time = temperature_controller_instance.last_decision_time[decision_key]

    # Simulate time advancing just past the decision interval
    with patch('time.monotonic', return_value=original_last_decision_time + temperature_controller_instance.decision_interval + 0.1):
        await temperature_controller_instance.execute(sensor_data_high, [exhaust_control], mock_command_queue)
        mock_exhaust_fan.set_action.assert_called_once_with(Action.DOWN)

    # Overall, mock_exhaust_fan.set_action should have been called twice in total for this test
    # First call, then second call after interval.
    # But since we reset in between, the check above is fine.
    # If we didn't reset:
    # assert mock_exhaust_fan.set_action.call_count == 2
    # This test confirms the interval logic for repeated calls under the same condition.

@pytest.mark.asyncio
async def test_controller_registration_and_device_dependency(temperature_controller_instance: TemperatureController, mock_exhaust_fan: AsyncMock):
    """Test that the controller is registered and depends on the correct device."""
    assert temperature_controller_instance.name in CONTROLLER_REGISTRY
    assert CONTROLLER_REGISTRY[temperature_controller_instance.name] is temperature_controller_instance

    # Check if the controller correctly identifies its dependent device (exhaust_fan)
    # This might depend on TemperatureController's internal logic for device discovery.
    # Assuming it looks up "exhaust_fan" in DEVICE_REGISTRY.
    # The fixture already ensures mock_exhaust_fan is in DEVICE_REGISTRY.

    # If TemperatureController has an explicit list of devices it manages:
    # assert "exhaust_fan" in temperature_controller_instance.managed_devices_ids (or similar attribute)
    # For now, this test mostly verifies fixture setup.
    assert "exhaust_fan" in DEVICE_REGISTRY
    assert DEVICE_REGISTRY["exhaust_fan"] is mock_exhaust_fan
    # Further checks could involve inspecting how TemperatureController uses the device.
    # The execute tests already cover interaction.

# Ensure the mock_command_queue fixture is available if any test needs to assert items on it,
# though these specific tests focus on device actions.

# To make this runnable, ensure that `app.core.controller`, `app.core.device`, `app.core.models`
# are structured such that these imports work.
# Also, the `TemperatureController` needs to be implemented to react to `SensorData`
# and call `set_action` on devices listed in `Control` objects or fetched from `DEVICE_REGISTRY`.
# The `config.growth_phase` patch target assumes `app.core.controller.config.growth_phase`.
# If `TemperatureController` takes `config` in `__init__`, the fixture needs to pass it.
# Let's assume for now `TemperatureController` uses a global config object as patched.

# The `decision_interval` in the base `Controller` class is `5` seconds.
# The `TemperatureController` might override this or take it as an `__init__` param.
# I've updated the fixture to pass `decision_interval` during instantiation.

print("app/tests/controllers/test_temperature.py created.")

# Note on TemperatureController implementation assumptions for these tests:
# 1. It fetches the 'exhaust_fan' device from DEVICE_REGISTRY.
# 2. It uses `config.growth_phase.TEMP_MIDDLE` and a `self.tolerance` attribute.
#    (Assuming self.tolerance is hardcoded or derived, e.g., TEMPERATURE_TOLERANCE = 2.0).
#    The problem description implies `temperature_tolerance` is a known value.
#    Let's assume TemperatureController is initialized or has a default for this tolerance.
#    For tests, it's better if this tolerance is also configurable or clearly defined.
#    The tests currently use a local `TEMPERATURE_TOLERANCE`. The controller should ideally use this too.
#    If `TemperatureController` has `self.tolerance`, it should be set.
#    Let's assume `TemperatureController` has a `self.tolerance` defaulting to `2.0` or set via config.
#    The patch `patch('app.core.controller.config.growth_phase', TEST_CONFIG)` should make `TEST_CONFIG`
#    available to the controller if it reads from `config.growth_phase`.
#    The `TemperatureController` itself would need to define its `self.tolerance`.
#    Let's add `temperature_tolerance` to `PhaseConfig` and `MockGrowthPhaseConfig`.

# Re-checking PhaseConfig and Controller logic:
# Controller base class has `decision_interval`. TemperatureController uses it.
# TemperatureController has its own `temperature_tolerance` attribute.
# Let's ensure this is consistent. The problem states `temperature_tolerance` without specifying where it comes from.
# I will assume `TemperatureController` has an attribute `self.temperature_tolerance`.
# I'll set it in the fixture for predictability.

# The `MockGrowthPhaseConfig` should include `TEMPERATURE_TOLERANCE` if the controller
# is expected to get it from the phase config. If not, `TemperatureController` must define it.
# Let's add it to `MockGrowthPhaseConfig` and assume `TemperatureController` uses it.

# Modifying MockGrowthPhaseConfig and fixture slightly.
# No, the `TemperatureController` itself defines `self.temperature_tolerance = 2.0`.
# So, `TEST_CONFIG` doesn't need it. The `TEMPERATURE_TOLERANCE` const here is just for test calculations.
# This is fine.

```
