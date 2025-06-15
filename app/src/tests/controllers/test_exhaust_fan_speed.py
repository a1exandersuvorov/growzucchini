import pytest

from growzucchini.controllers.exhaust_fan_speed import ExhaustFanSpeedController
from growzucchini.core.sensor_data import State
from tests.test_utils import get_test_sensor_data

rpm = 900.0


@pytest.fixture
def controller():
    return ExhaustFanSpeedController()


@pytest.mark.asyncio
async def test_rpm_value_transmitted_to_device(ctx, controller):
    sensor_data = get_test_sensor_data(ctx.ctrl, rpm)

    await controller(sensor_data, ctx.command_queue)

    ctx.device_mock.assert_awaited_once_with(State(rpm), ctx.ctrl, ctx.command_queue)


@pytest.mark.asyncio
async def test_invalid_device(ctx, controller):
    ctx.ctrl.device = "unknown"
    sensor_data = get_test_sensor_data(ctx.ctrl, rpm)

    # Should print error but not raise.
    await controller(sensor_data, ctx.command_queue)

    # Sensor readings should be transmitted to the device, but are not.
    ctx.device_mock.assert_not_called()
