import pytest
from unittest.mock import MagicMock, patch

from influxdb_client import Point

from katomato.core.metrics.influxdb_publisher import influx_ingestion
from katomato.core.sensor_data import SensorData


@pytest.fixture
def sample_sensor_data():
    return SensorData(
        sensor="temp",
        value=25.5,
        unit="C",
        label="Temperature",
        controls=[]
    )


def test_influx_ingestion_wrapper(sample_sensor_data):
    mock_func = MagicMock(return_value="done")

    # Apply the wrapper manually
    wrapped_func = influx_ingestion(mock_func)

    with patch("katomato.core.metrics.influxdb_publisher.write_api.write") as mock_write:
        result = wrapped_func(sample_sensor_data)

        # Assert wrapped function was called
        mock_func.assert_called_once_with(sample_sensor_data)

        # Assert Influx write was called
        mock_write.assert_called_once()
        args, kwargs = mock_write.call_args

        assert "record" in kwargs
        rec = kwargs["record"]
        assert isinstance(rec, Point)

        line = rec.to_line_protocol()
        assert "sensor=temp" in line
        assert 'label="Temperature"' in line
        assert 'unit="C"' in line
        assert "value=25.5" in line

        # Return value passed through correctly
        assert result == "done"
