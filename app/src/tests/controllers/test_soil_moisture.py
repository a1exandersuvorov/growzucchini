import time
from unittest.mock import patch, AsyncMock

import pytest

from growzucchini.config import config
from growzucchini.controllers.soil_moisture import SoilMoistureController
from growzucchini.core.registry import Action
from tests.test_utils import get_test_sensor_data


@pytest.fixture
def controller():
    soil_moisture_controller = SoilMoistureController()
    soil_moisture_controller.last_decision_time = time.monotonic() - soil_moisture_controller.decision_interval * 2
    return soil_moisture_controller


@pytest.mark.asyncio
async def test_soil_moisture_below_acceptable_value(ctx, controller):
    # Sensor readings below acceptable value
    sensor_data = get_test_sensor_data(ctx.mock_ctrl,
                                       config.growth_phase.SOIL_MOISTURE_FLOOR * 10 + controller.soil_moisture_tolerance)

    await controller(sensor_data, ctx.command_queue)

    ctx.mock_device.assert_awaited_once_with(Action.UP, ctx.mock_ctrl, ctx.command_queue)


@pytest.mark.asyncio
async def test_soil_moisture_in_acceptable_range(ctx, controller):
    # Sensor readings is within acceptable range
    sensor_data = get_test_sensor_data(ctx.mock_ctrl,
                                       (config.growth_phase.SOIL_MOISTURE_FLOOR + controller.soil_moisture_tolerance * 2) * 10)

    await controller(sensor_data, ctx.command_queue)

    ctx.mock_device.assert_not_called()


@pytest.mark.asyncio
async def test_invalid_device(ctx, controller):
    ctx.mock_ctrl.device = "unknown"
    # Sensor readings below acceptable value
    sensor_data = get_test_sensor_data(ctx.mock_ctrl,
                                       config.growth_phase.SOIL_MOISTURE_FLOOR * 10 + controller.soil_moisture_tolerance)

    # Should print error but not raise
    await controller(sensor_data, ctx.command_queue)

    # Sensor readings below acceptable value, but action hasn't been triggered
    ctx.mock_device.assert_not_called()


@pytest.mark.asyncio
async def test_delay_in_decision_making(ctx, controller):
    controller.last_decision_time = time.monotonic()
    # Sensor readings below acceptable value
    sensor_data = get_test_sensor_data(ctx.mock_ctrl,
                                       config.growth_phase.SOIL_MOISTURE_FLOOR * 10 + controller.soil_moisture_tolerance)

    await controller(sensor_data, ctx.command_queue)

    # Sensor readings below acceptable value, but action hasn't been triggered
    ctx.mock_device.assert_not_called()
