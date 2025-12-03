from unittest.mock import patch, MagicMock

import pytest

from katomato.devices.water_pump import WaterPump
from tests.test_utils import get_test_sensor_data


@pytest.mark.asyncio
async def test_estimate_runtime_calculates_correctly(ctx):
    sensor_value = 40.0
    target_moisture = 60.0
    flow_rate = 2.5 / 60  # liters/seconds
    pot_volume = 2  # liters

    expected_runtime = ((target_moisture - sensor_value) / 100) * (pot_volume / flow_rate)

    sensor_data = get_test_sensor_data(ctx.mock_ctrl, sensor_value)

    with patch("katomato.devices.water_pump.get_hardware_config") as mock_hw_config:
        mock_hw_config.return_value = {
            "WaterPump": MagicMock(
                FLOW_RATE=flow_rate,
                POT_VOLUME=pot_volume,
            )
        }

        pump = WaterPump()
        result = await pump.estimate_runtime(sensor_data)

        assert result == pytest.approx(expected_runtime, rel=9.6)
