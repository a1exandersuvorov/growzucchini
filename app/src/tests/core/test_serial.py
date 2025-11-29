import asyncio
import os

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from katosup.core.serial import ArduinoProtocol


@pytest.fixture
def command_queue():
    return asyncio.Queue()


@pytest.fixture
def mock_dispatcher():
    with patch("katosup.core.serial.controller_dispatcher") as mock:
        yield mock


@pytest.fixture
def mock_get_sensor_data():
    with patch("katosup.core.serial.get_sensor_data") as mock:
        yield mock


@pytest.mark.asyncio
async def test_data_received_valid_sensor(command_queue, mock_dispatcher, mock_get_sensor_data):
    mock_sensor_data = MagicMock()
    mock_sensor_data.sensor = "temp"
    mock_get_sensor_data.return_value = mock_sensor_data

    protocol = ArduinoProtocol(command_queue)
    protocol.data_received(b"temp,23.5\n")

    mock_dispatcher.assert_called_once_with(mock_sensor_data, command_queue)


@pytest.mark.asyncio
async def test_data_received_error_sensor(command_queue, mock_get_sensor_data, caplog):
    mock_sensor_data = MagicMock()
    mock_sensor_data.sensor = "error"
    mock_sensor_data.value = "something failed"
    mock_get_sensor_data.return_value = mock_sensor_data

    protocol = ArduinoProtocol(command_queue)
    protocol.data_received(b"error,something failed\n")

    assert any("Arduino error: something failed" in message for message in caplog.messages)


@pytest.mark.asyncio
async def test_connection_made_sets_transport(command_queue):
    protocol = ArduinoProtocol(command_queue)
    mock_transport = MagicMock()
    protocol.connection_made(mock_transport)
    assert protocol.transport == mock_transport


@pytest.mark.asyncio
async def test_connection_lost_triggers_reconnect(command_queue):
    mock_reconnect = AsyncMock()
    protocol = ArduinoProtocol(command_queue, on_connection_lost=mock_reconnect)
    protocol.connection_lost(Exception("Test disconnect"))
    await asyncio.sleep(0.01)  # Let event loop process the task
    mock_reconnect.assert_awaited_once()


@pytest.mark.asyncio
async def test_send_command_sends_data(command_queue):
    protocol = ArduinoProtocol(command_queue)
    mock_transport = MagicMock()
    protocol.transport = mock_transport

    await protocol.send_command("123")
    mock_transport.write.assert_called_once_with(b"123")


@pytest.mark.asyncio
async def test_send_command_empty(command_queue, caplog):
    protocol = ArduinoProtocol(command_queue)
    await protocol.send_command("")

    assert any("Empty command ignored." in message for message in caplog.messages)


@pytest.mark.asyncio
async def test_buffer_partial_and_multiple_lines(command_queue, mock_dispatcher, mock_get_sensor_data):
    sensor_data_1 = MagicMock(sensor="temp")
    sensor_data_2 = MagicMock(sensor="hum")
    mock_get_sensor_data.side_effect = [sensor_data_1, sensor_data_2]

    protocol = ArduinoProtocol(command_queue)
    # Simulate receiving partial + two full messages
    protocol.data_received(b"temp,23.5\nhum,45.3\nincompl")
    assert protocol.buffer == "incompl"
    assert mock_dispatcher.call_count == 2


@pytest.mark.asyncio
async def test_debug_mode(command_queue, caplog):
    caplog.set_level("INFO")
    with patch.dict(os.environ, {"APP_MODE": "arduino_debug"}):
        protocol = ArduinoProtocol(command_queue)
        protocol.data_received(b"some_debug_line\n")

        assert any("Debug mode: some_debug_line" in message for message in caplog.messages)
