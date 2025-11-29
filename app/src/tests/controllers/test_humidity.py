import pytest

from katosup.config import config
from katosup.controllers.humidity import HumidityController
from katosup.core.registry import Action
from tests.test_utils import get_test_sensor_data


@pytest.fixture
def controller():
    return HumidityController()


@pytest.mark.asyncio
async def test_humidity_above_acceptable_value(ctx, controller):
    # Sensor readings above acceptable value
    sensor_data = get_test_sensor_data(ctx.mock_ctrl, config.growth_phase.HUM_CEIL - controller.hum_tolerance + 0.01)

    await controller(sensor_data, ctx.command_queue)

    ctx.mock_device.assert_awaited_once_with(Action.DOWN, ctx.mock_ctrl, ctx.command_queue)


@pytest.mark.asyncio
async def test_humidity_below_acceptable_value(ctx, controller):
    # Sensor readings below acceptable value
    sensor_data = get_test_sensor_data(ctx.mock_ctrl, controller.hum_mid - controller.hum_tolerance)

    await controller(sensor_data, ctx.command_queue)

    ctx.mock_device.assert_awaited_once_with(Action.UP, ctx.mock_ctrl, ctx.command_queue)


@pytest.mark.asyncio
async def test_humidity_value_in_acceptable_range(ctx, controller):
    # Sensor readings is within acceptable range
    sensor_data = get_test_sensor_data(ctx.mock_ctrl, controller.hum_mid)
    await controller(sensor_data, ctx.command_queue)

    sensor_data = get_test_sensor_data(ctx.mock_ctrl, config.growth_phase.HUM_CEIL - controller.hum_tolerance)
    await controller(sensor_data, ctx.command_queue)

    sensor_data = get_test_sensor_data(ctx.mock_ctrl, controller.hum_mid - controller.hum_tolerance + 0.01)
    await controller(sensor_data, ctx.command_queue)

    ctx.mock_device.assert_not_called()


@pytest.mark.asyncio
async def test_invalid_device(ctx, controller):
    ctx.mock_ctrl.device = "unknown"
    # Sensor readings below acceptable value
    sensor_data = get_test_sensor_data(ctx.mock_ctrl, controller.hum_mid - controller.hum_tolerance)

    # Should print error but not raise
    await controller(sensor_data, ctx.command_queue)

    # Sensor readings below acceptable value, but action hasn't been triggered
    ctx.mock_device.assert_not_called()
