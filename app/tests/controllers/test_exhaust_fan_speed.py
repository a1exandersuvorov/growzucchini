import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, ANY

# Assuming ExhaustFanSpeedController is in app.core.controller for consistency
# and other necessary classes are also in app.core
from app.core.controller import ExhaustFanSpeedController, CONTROLLER_REGISTRY
from app.core.device import DEVICE_REGISTRY
from app.core.models import SensorData, Control, State, Device # Assuming Device is needed for spec

# Import mock_command_queue fixture (pytest will find it in conftest.py)
# from app.tests.conftest import mock_command_queue

@pytest.fixture
def mock_exhaust_fan():
    """Provides a mock exhaust fan device."""
    # The controller calls the device instance itself, so the instance needs to be callable (AsyncMock handles this)
    # and have a 'name' attribute for some internal controller/device_manager logic.
    fan_device = AsyncMock(spec=Device) # Using Device for spec helps ensure it behaves like a device
    fan_device.name = "exhaust_fan" # Controller's __init__ might use this to find the device
    fan_device.device_id = "exhaust_fan" # For registry key
    yield fan_device

@pytest.fixture
def exhaust_fan_speed_controller_instance(mock_exhaust_fan: AsyncMock):
    """
    Provides an instance of ExhaustFanSpeedController with a clean registry state
    and the mock_exhaust_fan registered.
    """
    DEVICE_REGISTRY.clear()
    CONTROLLER_REGISTRY.clear()

    # Register the mock fan. The controller expects to find it in DEVICE_REGISTRY.
    DEVICE_REGISTRY[mock_exhaust_fan.device_id] = mock_exhaust_fan

    # Instantiate ExhaustFanSpeedController.
    # Based on its actual code, it doesn't take config for RPM target/tolerance,
    # it just forwards the sensor value.
    # It might take a decision_interval, but the provided code doesn't show its __init__.
    # Assuming a default __init__ or one that takes interval.
    # For this test, interval isn't directly tested, so default is fine.
    controller = ExhaustFanSpeedController() # Or ExhaustFanSpeedController(decision_interval=5)

    # Register the controller. The 'ef' name is its default.
    CONTROLLER_REGISTRY[controller.name] = controller

    yield controller

    # Cleanup
    if controller.name in CONTROLLER_REGISTRY:
        del CONTROLLER_REGISTRY[controller.name]
    if mock_exhaust_fan.device_id in DEVICE_REGISTRY:
        del DEVICE_REGISTRY[mock_exhaust_fan.device_id]

# --- Test Case ---

@pytest.mark.asyncio
async def test_forwards_rpm_value_as_state(
    exhaust_fan_speed_controller_instance: ExhaustFanSpeedController, # Get controller
    mock_exhaust_fan: AsyncMock, # Get the specific mock instance used in the fixture
    mock_command_queue: asyncio.Queue # Get the command queue
):
    """
    Test that ExhaustFanSpeedController forwards the RPM sensor value as State
    to the exhaust_fan device.
    """
    rpm_value = 1980
    # The Control object from SensorData is what's passed to the device.
    control_data = Control(pin=9, type='analog', device_id='exhaust_fan', current_value=0) # current_value is arbitrary here

    sensor_data = SensorData(
        sensor='ef', # Matches controller name/type
        label='Exhaust Fan Speed',
        value=rpm_value,
        unit='rpm',
        controls=[control_data] # List of controls associated with this sensor reading
    )

    # Call the controller's __call__ method (or execute, depending on base class)
    # The prompt indicates: await controller(sensor_data, mock_command_queue)
    # This implies the controller instance itself is callable.
    # Let's assume the base Controller class has an __await__ or a relevant method
    # that `await controller(...)` resolves to.
    # More typically, it would be `await controller.execute(...)`
    # Given the actual code for ExhaustFanSpeedController's parent:
    # `async def __call__(self, sensor_data: SensorData, command_queue: asyncio.Queue):`
    # So, `await controller(sensor_data, mock_command_queue)` is correct.

    await exhaust_fan_speed_controller_instance(sensor_data, mock_command_queue)

    # Assert that the mock_exhaust_fan device was called.
    # The ExhaustFanSpeedController's relevant code:
    #   `device = DEVICE_REGISTRY[control.device_id]`
    #   `await device(State(sensor_data.value), control, command_queue)`

    mock_exhaust_fan.assert_called_once()

    # Assert the arguments of the call.
    # The first argument should be State(rpm_value).
    # The second argument should be the control_data object.
    # The third argument should be the command_queue.

    # Retrieve the arguments from the mock call
    args, kwargs = mock_exhaust_fan.call_args

    # Check the first argument (State object)
    assert isinstance(args[0], State), "First argument was not a State object"
    assert args[0].value == rpm_value, f"State value was {args[0].value}, expected {rpm_value}"

    # Check the second argument (Control object)
    assert args[1] is control_data, "Second argument was not the expected Control object"

    # Check the third argument (command_queue)
    assert args[2] is mock_command_queue, "Third argument was not the expected command queue"

print("app/tests/controllers/test_exhaust_fan_speed.py created with revised logic.")

```
