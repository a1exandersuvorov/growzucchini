import json
from datetime import datetime, timezone
from functools import wraps

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

from growzucchini.config import config
from growzucchini.core.sensor_data import SensorData

client = InfluxDBClient(
    url=config.INFLUX_URL, token=config.INFLUX_TOKEN, org=config.INFLUX_ORG
)
write_api = client.write_api(write_options=SYNCHRONOUS)


def influx_ingestion(func):
    @wraps(func)
    def wrapper(*args):
        arg = args[0]
        if isinstance(arg, str):
            try:
                arg = json.loads(arg)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON")
        if isinstance(arg, dict):
            data = SensorData(**arg)
        else:
            data = arg

        # Send to InfluxDB
        point = (
            Point("sensor_data")
            .tag("sensor", data.sensor)
            .field("value", float(data.value))
            .field("label", data.label)  # metadata, no aggregation
            .field("unit", data.unit)  # metadata, no aggregation
            .time(datetime.now(timezone.utc))
        )
        write_api.write(
            bucket=config.INFLUX_BUCKET, org=config.INFLUX_ORG, record=point
        )

        return func(*args)

    return wrapper
