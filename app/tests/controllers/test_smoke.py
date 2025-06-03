import asyncio
import pytest
from unittest.mock import MagicMock, patch

# Assuming SmokeDetectionController is in app.core.controller for consistency.
# Adjust if it's in a different location like app.growzucchini.controllers.
from app.core.controller import SmokeDetectionController, CONTROLLER_REGISTRY
from app.core.device import DEVICE_REGISTRY # Imported for consistency in fixture cleanup
from app.core.models import SensorData, Control # Control might not be strictly needed if controls list is empty

# Import mock_command_queue fixture (pytest will find it in conftest.py)
# from app.tests.conftest import mock_command_queue

@pytest.fixture
def smoke_controller_instance():
    """
    Provides an instance of SmokeDetectionController with a clean registry state.
    """
    # Clear registries for test isolation
    DEVICE_REGISTRY.clear() # Clearing for consistency, though SmokeController may not use devices
    CONTROLLER_REGISTRY.clear()

    # Instantiate SmokeDetectionController.
    # Based on its code, it doesn't require special __init__ args beyond defaults.
    controller = SmokeDetectionController()

    # Register the controller. The 'smoke' name is its default.
    CONTROLLER_REGISTRY[controller.name] = controller

    yield controller

    # Cleanup
    if controller.name in CONTROLLER_REGISTRY:
        del CONTROLLER_REGISTRY[controller.name]
    # No devices explicitly registered by this fixture, so DEVICE_REGISTRY cleanup is just a reset.

# --- Test Cases ---

@pytest.mark.asyncio
async def test_smoke_controller_runs_without_error(
    smoke_controller_instance: SmokeDetectionController,
    mock_command_queue: asyncio.Queue
):
    """
    Test that SmokeDetectionController can be called without raising an error.
    Its current functionality is to print a message.
    """
    # The actual values in SensorData don't matter for SmokeDetectionController logic
    # as it doesn't process them, but we need a valid SensorData object.
    sensor_data = SensorData(
        sensor='smoke',
        label='Smoke Detector',
        value=1,  # Arbitrary value
        unit='detection', # Arbitrary unit
        controls=[] # No specific controls needed for this controller
    )

    # The controller's __call__ method is `async def __call__(self, sensor_data: SensorData, command_queue: asyncio.Queue):`
    # It currently just prints. If it completed without exceptions, the test passes this aspect.
    try:
        # Patch builtins.print to check if it was called, if desired.
        # For this test, primarily ensuring it runs without error.
        with patch('builtins.print') as mock_print:
            await smoke_controller_instance(sensor_data, mock_command_queue)
            # Optionally, assert print was called if that's a critical side-effect to verify.
            # For example: mock_print.assert_called()
            # Or with specific text if the text is stable and important:
            # mock_print.assert_any_call(f"SmokeDetectionController received data: {sensor_data}")
            # However, the prompt said to skip asserting on print for now.
    except Exception as e:
        pytest.fail(f"SmokeDetectionController call raised an exception: {e}")

@pytest.mark.asyncio
async def test_smoke_controller_registration(
    smoke_controller_instance: SmokeDetectionController
):
    """
    Test that the SmokeDetectionController instance is correctly registered
    in the CONTROLLER_REGISTRY.
    """
    assert CONTROLLER_REGISTRY.get('smoke') is smoke_controller_instance, \
        "SmokeDetectionController instance was not found in CONTROLLER_REGISTRY under 'smoke' key or was not the same instance."

print("app/tests/controllers/test_smoke.py created.")

```
