import asyncio
import contextlib
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from growzucchini.core.dispatcher import command_dispatcher, controller_dispatcher
from growzucchini.core.sensor_data import SensorData
from growzucchini.core.registry import CONTROLLER_REGISTRY


@pytest.fixture
def command_queue():
    return asyncio.Queue()


@pytest.fixture
def fake_arduino_protocol():
    protocol = AsyncMock()
    return protocol


@pytest.fixture
def fake_shutdown_handler():
    handler = MagicMock()
    return handler


@pytest.mark.asyncio
async def test_command_dispatcher_executes_valid_command(command_queue, fake_arduino_protocol, fake_shutdown_handler):
    await command_queue.put(json.dumps({
        "command": "set",
        "pin": 5,
        "type": "digital",
        "value": 1
    }))

    task = asyncio.create_task(command_dispatcher(command_queue, fake_arduino_protocol, fake_shutdown_handler))

    await asyncio.sleep(0.1)
    task.cancel()

    fake_arduino_protocol.send_command.assert_awaited_once()


@pytest.mark.asyncio
async def test_command_dispatcher_handles_invalid_json(command_queue, fake_arduino_protocol, fake_shutdown_handler,
                                                       caplog):
    await command_queue.put("invalid-json")

    task = asyncio.create_task(command_dispatcher(command_queue, fake_arduino_protocol, fake_shutdown_handler))

    await asyncio.sleep(0.1)
    task.cancel()

    assert any("Invalid command JSON" in message for message in caplog.messages)


@pytest.mark.asyncio
async def test_command_dispatcher_switches_phase(command_queue, fake_arduino_protocol, fake_shutdown_handler):
    mock_phase = MagicMock()

    with patch("growzucchini.core.dispatcher.config.get_growth_phases", return_value={"veg": mock_phase}), \
            patch("growzucchini.core.dispatcher.config.switch_growth_phase") as switch_mock:
        await command_queue.put(json.dumps({"command": "phase", "name": "veg"}))

        task = asyncio.create_task(command_dispatcher(command_queue, fake_arduino_protocol, fake_shutdown_handler))

        await asyncio.sleep(0.1)
        task.cancel()

        switch_mock.assert_called_once_with(mock_phase)


@pytest.mark.asyncio
async def test_command_dispatcher_unknown_phase(command_queue, fake_arduino_protocol, fake_shutdown_handler, caplog):
    caplog.set_level("WARNING")
    with patch("growzucchini.core.dispatcher.config.get_growth_phases", return_value={}):
        await command_queue.put(json.dumps({"command": "phase", "name": "unknown"}))

        task = asyncio.create_task(command_dispatcher(command_queue, fake_arduino_protocol, fake_shutdown_handler))
        await asyncio.sleep(0.1)
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task

        assert any("Unknown phase: unknown" in message for message in caplog.messages)


@pytest.mark.asyncio
async def test_command_dispatcher_triggers_shutdown(command_queue, fake_arduino_protocol, fake_shutdown_handler):
    await command_queue.put(json.dumps({"command": "exit"}))

    await command_dispatcher(command_queue, fake_arduino_protocol, fake_shutdown_handler)

    fake_shutdown_handler.request_shutdown.assert_called_once()


def test_controller_dispatcher_found_controller():
    command_queue = asyncio.Queue()
    mock_controller = AsyncMock()
    sensor_data = SensorData(sensor="temp", value=25, unit="C", label="Temperature", controls=[])

    CONTROLLER_REGISTRY["temp"] = mock_controller

    with patch("asyncio.create_task") as create_task_mock:
        controller_dispatcher(sensor_data, command_queue)

    create_task_mock.assert_called_once()


def test_controller_dispatcher_controller_not_found(caplog):
    command_queue = asyncio.Queue()
    sensor_data = SensorData(sensor="unknown_sensor", value=123, unit="x", label="x", controls=[])

    if "unknown_sensor" in CONTROLLER_REGISTRY:
        del CONTROLLER_REGISTRY["unknown_sensor"]

    controller_dispatcher(sensor_data, command_queue)

    assert any("No controller found for: unknown_sensor" in message for message in caplog.messages)
