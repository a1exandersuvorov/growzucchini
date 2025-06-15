import pytest

from growzucchini.config import config
from growzucchini.controllers.humidity import HumidityController
from growzucchini.core.registry import Action
from tests.test_utils import get_test_sensor_data


@pytest.fixture
def controller():
    return HumidityController()


@pytest.mark.asyncio
async def test_humidity_above_acceptable_value(ctx, controller):
    # Sensor readings above acceptable value.
    sensor_data = get_test_sensor_data(ctx.ctrl, config.growth_phase.HUM_CEIL - controller.hum_tolerance + 0.01)

    await controller(sensor_data, ctx.command_queue)

    ctx.device_mock.assert_awaited_once_with(Action.DOWN, ctx.ctrl, ctx.command_queue)


@pytest.mark.asyncio
async def test_humidity_below_acceptable_value(ctx, controller):
    # Sensor readings below acceptable value.
    sensor_data = get_test_sensor_data(ctx.ctrl, controller.hum_mid - controller.hum_tolerance)

    await controller(sensor_data, ctx.command_queue)

    ctx.device_mock.assert_awaited_once_with(Action.UP, ctx.ctrl, ctx.command_queue)


@pytest.mark.asyncio
async def test_humidity_value_in_acceptable_range(ctx, controller):
    # Sensor readings is within acceptable range.
    sensor_data = get_test_sensor_data(ctx.ctrl, controller.hum_mid)
    await controller(sensor_data, ctx.command_queue)

    sensor_data = get_test_sensor_data(ctx.ctrl, config.growth_phase.HUM_CEIL - controller.hum_tolerance)
    await controller(sensor_data, ctx.command_queue)

    sensor_data = get_test_sensor_data(ctx.ctrl, controller.hum_mid - controller.hum_tolerance + 0.01)
    await controller(sensor_data, ctx.command_queue)

    ctx.device_mock.assert_not_called()


@pytest.mark.asyncio
async def test_invalid_device(ctx, controller):
    ctx.ctrl.device = "unknown"
    # Sensor readings below acceptable value.
    sensor_data = get_test_sensor_data(ctx.ctrl, controller.hum_mid - controller.hum_tolerance)

    # Should print error but not raise.
    await controller(sensor_data, ctx.command_queue)

    # Sensor readings below acceptable value, but action hasn't been triggered.
    ctx.device_mock.assert_not_called()
