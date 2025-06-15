import pytest

from growzucchini.controllers.smoke import SmokeDetectionController
from growzucchini.core.registry import Action
from tests.test_utils import get_test_sensor_data

sensor_val = 1.0


@pytest.fixture
def controller():
    return SmokeDetectionController()


@pytest.mark.asyncio
async def test_smoke_detected(ctx, controller):
    sensor_data = get_test_sensor_data(ctx.ctrl, sensor_val)

    await controller(sensor_data, ctx.command_queue)

    ctx.device_mock.assert_awaited_once_with(Action.DOWN, ctx.ctrl, ctx.command_queue)


@pytest.mark.asyncio
async def test_invalid_device(ctx, controller):
    ctx.ctrl.device = "unknown"
    sensor_data = get_test_sensor_data(ctx.ctrl, sensor_val)

    # Should print error but not raise.
    await controller(sensor_data, ctx.command_queue)

    # Sensor readings should be transmitted to the device, but are not.
    ctx.device_mock.assert_not_called()
