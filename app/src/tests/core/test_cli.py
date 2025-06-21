import asyncio
import json
from unittest.mock import patch

import pytest

from growzucchini.core.cli import handle_cli
from growzucchini.core.utils.command_util import get_sensor_data


@pytest.mark.asyncio
async def test_handle_cli_phase_command():
    queue = asyncio.Queue()

    with patch("builtins.input", side_effect=["phase vegetative", "exit"]):
        task = asyncio.create_task(handle_cli(queue))
        await task  # Await normally since it should exit via "exit"

    phase_cmd = await queue.get()
    assert json.loads(phase_cmd) == {"command": "phase", "name": "vegetative"}

    exit_cmd = await queue.get()
    assert json.loads(exit_cmd) == {"command": "exit"}


@pytest.mark.asyncio
async def test_handle_cli_exit_command():
    queue = asyncio.Queue()

    with patch("builtins.input", side_effect=["exit"]):
        await handle_cli(queue)
        cmd = await queue.get()
        assert json.loads(cmd) == {"command": "exit"}


@pytest.mark.asyncio
async def test_handle_cli_invalid_command_format(caplog):
    queue = asyncio.Queue()

    with patch("builtins.input", side_effect=["invalid command", "exit"]):
        task = asyncio.create_task(handle_cli(queue))
        await task  # Await normally since it should exit via "exit"

        assert any("Invalid input" in message for message in caplog.messages)


@patch("growzucchini.core.cli.controller_dispatcher")
@pytest.mark.asyncio
async def test_handle_cli_sim_command_dispatch(mock_dispatcher):
    queue = asyncio.Queue()
    sim_data = (
        '{"sensor": "ef", "label": "Exhaust Fan Speed", "value": 0, "unit": "rpm", '
        '"controls": [{"pin": 4, "type": "analog", "device": "exhaust_fan"}]}'
    )

    sensor_data = get_sensor_data(sim_data)

    with patch("builtins.input", side_effect=["sim " + sim_data, "exit"]):
        task = asyncio.create_task(handle_cli(queue))
        await task

    mock_dispatcher.assert_called_once_with(sensor_data, queue)
    assert json.loads(await queue.get()) == {"command": "exit"}
