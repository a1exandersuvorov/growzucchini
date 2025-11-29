import pytest

from katosup.controllers.exhaust_fan_speed import ExhaustFanSpeedController
from katosup.core.sensor_data import State
from tests.test_utils import get_test_sensor_data

rpm = 900.0


@pytest.fixture
def controller():
    return ExhaustFanSpeedController()


@pytest.mark.asyncio
async def test_rpm_value_transmitted_to_device(ctx, controller):
    sensor_data = get_test_sensor_data(ctx.mock_ctrl, rpm)

    await controller(sensor_data, ctx.command_queue)

    ctx.mock_device.assert_awaited_once_with(State(rpm), ctx.mock_ctrl, ctx.command_queue)


@pytest.mark.asyncio
async def test_invalid_device(ctx, controller):
    ctx.mock_ctrl.device = "unknown"
    sensor_data = get_test_sensor_data(ctx.mock_ctrl, rpm)

    # Should print error but not raise
    await controller(sensor_data, ctx.command_queue)

    # Sensor readings should be transmitted to the device, but are not
    ctx.mock_device.assert_not_called()
