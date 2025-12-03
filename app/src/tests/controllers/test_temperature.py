import time

import pytest

from katomato.controllers.temperature import TemperatureController
from katomato.core.registry import Action
from tests.test_utils import get_test_sensor_data


@pytest.fixture
def controller():
    temperature_controller = TemperatureController()
    temperature_controller.last_decision_time = time.monotonic() - temperature_controller.decision_interval * 2
    return temperature_controller


@pytest.mark.asyncio
async def test_temperature_above_acceptable_value(ctx, controller):
    # Sensor readings above acceptable value
    sensor_data = get_test_sensor_data(ctx.mock_ctrl, controller.temp_mid + controller.temp_tolerance + 0.01)

    await controller(sensor_data, ctx.command_queue)

    ctx.mock_device.assert_awaited_once_with(Action.DOWN, ctx.mock_ctrl, ctx.command_queue)


@pytest.mark.asyncio
async def test_temperature_below_acceptable_value(ctx, controller):
    # Sensor readings below acceptable value
    sensor_data = get_test_sensor_data(ctx.mock_ctrl, controller.temp_mid - controller.temp_tolerance - 0.01)

    await controller(sensor_data, ctx.command_queue)

    ctx.mock_device.assert_awaited_once_with(Action.UP, ctx.mock_ctrl, ctx.command_queue)


@pytest.mark.asyncio
async def test_temperature_in_acceptable_range(ctx, controller):
    # Sensor readings is within acceptable range
    sensor_data = get_test_sensor_data(ctx.mock_ctrl, controller.temp_mid + controller.temp_tolerance)
    await controller(sensor_data, ctx.command_queue)

    sensor_data = get_test_sensor_data(ctx.mock_ctrl, controller.temp_mid - controller.temp_tolerance)
    await controller(sensor_data, ctx.command_queue)

    sensor_data = get_test_sensor_data(ctx.mock_ctrl, controller.temp_mid)
    await controller(sensor_data, ctx.command_queue)

    ctx.mock_device.assert_not_called()


@pytest.mark.asyncio
async def test_invalid_device(ctx, controller):
    ctx.mock_ctrl.device = "unknown"
    # Sensor readings above acceptable value
    sensor_data = get_test_sensor_data(ctx.mock_ctrl, controller.temp_mid + controller.temp_tolerance + 0.01)

    # Should print error but not raise
    await controller(sensor_data, ctx.command_queue)

    # Sensor readings above acceptable value, but action hasn't been triggered
    ctx.mock_device.assert_not_called()


@pytest.mark.asyncio
async def test_delay_in_decision_making(ctx, controller):
    controller.last_decision_time = time.monotonic()
    # Sensor readings above acceptable value
    sensor_data = get_test_sensor_data(ctx.mock_ctrl, controller.temp_mid + controller.temp_tolerance + 0.01)

    await controller(sensor_data, ctx.command_queue)

    # Sensor readings above acceptable value, but action hasn't been triggered
    ctx.mock_device.assert_not_called()
