import pytest
import time

from growzucchini.controllers.temperature import TemperatureController
from growzucchini.core.registry import Action
from tests.test_utils import get_test_sensor_data


@pytest.fixture
def controller():
    handler = TemperatureController()
    handler.last_decision_time = time.monotonic() - handler.decision_interval * 2
    return handler


@pytest.mark.asyncio
async def test_temperature_above_acceptable_value(ctx, controller):
    # Sensor readings above acceptable value.
    sensor_data = get_test_sensor_data(ctx.ctrl, controller.temp_mid + controller.temp_tolerance + 0.01)

    await controller(sensor_data, ctx.command_queue)

    ctx.device_mock.assert_awaited_once_with(Action.DOWN, ctx.ctrl, ctx.command_queue)


@pytest.mark.asyncio
async def test_temperature_below_acceptable_value(ctx, controller):
    # Sensor readings below acceptable value.
    sensor_data = get_test_sensor_data(ctx.ctrl, controller.temp_mid - controller.temp_tolerance - 0.01)

    await controller(sensor_data, ctx.command_queue)

    ctx.device_mock.assert_awaited_once_with(Action.UP, ctx.ctrl, ctx.command_queue)


@pytest.mark.asyncio
async def test_temperature_in_acceptable_range(ctx, controller):
    # Sensor readings is within acceptable range.
    sensor_data = get_test_sensor_data(ctx.ctrl, controller.temp_mid + controller.temp_tolerance)
    await controller(sensor_data, ctx.command_queue)

    sensor_data = get_test_sensor_data(ctx.ctrl, controller.temp_mid - controller.temp_tolerance)
    await controller(sensor_data, ctx.command_queue)

    sensor_data = get_test_sensor_data(ctx.ctrl, controller.temp_mid)
    await controller(sensor_data, ctx.command_queue)

    ctx.device_mock.assert_not_called()


@pytest.mark.asyncio
async def test_invalid_device(ctx, controller):
    ctx.ctrl.device = "unknown"
    # Sensor readings above acceptable value.
    sensor_data = get_test_sensor_data(ctx.ctrl, controller.temp_mid + controller.temp_tolerance + 0.01)

    # Should print error but not raise.
    await controller(sensor_data, ctx.command_queue)

    # Sensor readings above acceptable value, but action hasn't been triggered.
    ctx.device_mock.assert_not_called()


@pytest.mark.asyncio
async def test_delay_in_decision_making(ctx, controller):
    controller.last_decision_time = time.monotonic()
    # Sensor readings above acceptable value.
    sensor_data = get_test_sensor_data(ctx.ctrl, controller.temp_mid + controller.temp_tolerance + 0.01)

    await controller(sensor_data, ctx.command_queue)

    # Sensor readings above acceptable value, but action hasn't been triggered.
    ctx.device_mock.assert_not_called()
